from midiutil.MidiFile import NoteOff

from parsers.patterns import Pattern, Note
from midiutil import MIDIFile


class PatternToMidiExporter:

    # midi utils uses either ticks of beats (quarter notes) as time
    # beats are expressed in floats
    # tracker uses 1/16 of s note
    # so this value is a tracker step duration to use with MIDIUtil
    MIDI_16TH_NOTE_TIME_VALUE = 0.25

    def __init__(self, pattern: Pattern, tempo_bpm=120):

        self.pattern = pattern
        # patterns themselves do not store tempo information
        # as it is set globally for the whole song, so we just
        # go with whatever is passed to us
        self.tempo_bpm = tempo_bpm

    def get_list_of_instruments(self):

        instruments = set()

        for track in self.pattern.tracks:
            for step in track.steps:
                if step.instrument_number:
                    instruments.add(step.instrument_number)

        return sorted(instruments)

    @staticmethod
    def get_midi_note_value(note: Note):
        if note.is_empty():
            raise ValueError("Cannot get midi note value for empty note!")

        if note.is_off_fad_or_cut():
            raise ValueError("Cannot get midi note value for note off event!")

        # midi middle C (C4) is 60
        # tracker C4 is 48
        return note.value+12

    def generate_midi(self) -> MIDIFile:
        degrees = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number

        # tracker tracks are not actual tracks, but voices,
        # since every track can use any instrument at even given time and
        # every track is monophonic.
        # midi tracks typically represent different instruments and are polyphonic
        # so we should count number of instruments in pattern and use it as
        # number of tracks
        instruments = self.get_list_of_instruments()
        midi_tracks_count = len(instruments)

        track = 0
        channel = 0
        time = 0  # In beats (is it 4:4?)
        default_duration = 1  # In beats (is it 4:4?)
        tempo = 60  # In BPM
        default_volume = 127  # 0-127, as per the MIDI standard

        # this maps allows us to quickly find midi track for given instrument
        # this should be faster than calling instruments.indexOf()
        instrument_to_midi_track_map = {}

        midi_file = MIDIFile(midi_tracks_count)
        midi_file.addTempo(track=0, time=0, tempo=self.tempo_bpm)

        for i in range(len(instruments)):
            # todo: get actual track names from project file (or are they stored in instrument files?)
            # todo: instrument 48 is midi instrument 1 the next 15 are also midi instruments - set their names
            midi_file.addTrackName(track=i, time=0, trackName=f"Instrument {instruments[i]}")

            instrument_to_midi_track_map[instruments[i]] = i

        for track in self.pattern.tracks:

            for step_number in range(track.length):

                step = track.steps[step_number]

                if step.note.is_empty():
                    continue

                if step.note.is_off_fad_or_cut():
                    # adding note off event is complicated, it's easier to rely on duration
                    # argument for addNote
                    continue

                else:

                    # we've got a note
                    # check when the next note or NOTE OFF appears on this track
                    # so we can calculate note duration
                    note_end_position = None

                    # iterate the track from the next step till the end
                    # until we encounter a note
                    for inner_step_number in range(step_number+1, track.length):
                        inner_step = track.steps[inner_step_number]
                        if inner_step.note.is_off_fad_or_cut():
                            # found note break
                            note_end_position = inner_step_number
                            break
                        if not inner_step.note.is_empty():
                            # found next note - time to disable this one
                            note_end_position = inner_step_number
                            break

                    # if we haven't found anything, we'll just disable the note at
                    # the end of the pattern
                    if not note_end_position:
                        # make sure we disable the note after pattern ends and not at
                        # the last step of the pattern
                        note_end_position = track.length

                    duration = (note_end_position - step_number) * PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE


                    # TODO: add support for chord fx
                    # TODO: add support for arp fx

                    if step.get_arp():
                        # arpeggio
                        arp = step.get_arp()

                        notes_iterator = arp.get_notes_iterator()

                        # time at which each consequent note in arp starts playing
                        arp_note_start_time = step_number * PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE
                        # time at which we should stop arpeggiating
                        arp_end_time = note_end_position * PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE
                        # duration of each note in arpeggio
                        arp_note_duration = arp.division * PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE

                        for note in notes_iterator:
                            # every note has a length of arp division
                            # (arp division is basically number of 1/16steps each note is played,
                            # can be fractional)
                            # so we have to add notes playing after each other and stop ath the NOTE OFF/CUT/FAD
                            # event
                            # todo: also stop if step with arp value 0 is encountered (that's how tracker does it)
                            #  note that this step will not return arp as we check for value in get_arp,
                            #  so we'll probably need another method like has_arp_stop_event or something
                            #  that specifically check for arp effect with 0 value


                            # fixme: should it be just > instead of >=?
                            if arp_note_start_time >= arp_end_time:
                                # reached next note, CUT/FAD/OFF event
                                # or end of pattern (actually end of the patter probably should not
                                # end arp if there is a next pattern in song mode, but should do it if
                                # we are rendering just one pattern, since we have to end sending notes
                                # to midi file somewhere
                                break

                            # check that the  the note we are about to end won't end playing after
                            # intended place for the arp to stop (this usually happens with
                            # uneven divisions like 6, 1/3, etc.)
                            if arp_note_start_time + arp_note_duration >= arp_end_time:
                                # this is the last note in this arp
                                # and it's too long (going beyond note OFF/CUT/FAD or pattern end),
                                # so we going to jsut shorten its duration
                                arp_note_duration = arp_end_time - arp_note_start_time

                            midi_file.addNote(track=instrument_to_midi_track_map[step.instrument_number],
                                              channel=channel,
                                              pitch=PatternToMidiExporter.get_midi_note_value(note),
                                              time=arp_note_start_time,
                                              duration=arp_note_duration,
                                              # TODO: write velocity fx value if set (needs to be converted to 0...127!!!)
                                              volume=default_volume,
                                              )

                            # increment starting time for the next note
                            arp_note_start_time += arp_note_duration


                    elif step.get_chord():
                        # chord
                        chord = step.get_chord()
                        for note in chord.notes:
                            # TODO: make this DRY as this differs from default case with one note just by one argument
                            midi_file.addNote(track=instrument_to_midi_track_map[step.instrument_number],
                                              channel=channel,
                                              pitch=PatternToMidiExporter.get_midi_note_value(note),
                                              time=step_number * PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE,
                                              duration=duration,
                                              # TODO: write velocity fx value if set (needs to be converted to 0...127!!!)
                                              volume=default_volume,
                                              )

                    else:
                        # default case - just a regular single note playing
                        midi_file.addNote(track=instrument_to_midi_track_map[step.instrument_number],
                                          channel=channel,
                                          pitch=PatternToMidiExporter.get_midi_note_value(step.note),
                                          time=step_number*PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE,
                                          duration=duration,
                                          # TODO: write velocity fx value if set (needs to be converted to 0...127!!!)
                                          volume=default_volume,
                                          )

        return midi_file

    def write_midi_file(self, path: str):

        midi_file = self.generate_midi()

        with open(path, "wb") as output_file:
            midi_file.writeFile(output_file)



