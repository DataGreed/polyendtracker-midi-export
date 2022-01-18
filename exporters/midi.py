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
        last_processed_step_by_instrument = {}

        midi_file = MIDIFile(midi_tracks_count)
        midi_file.addTempo(track=0, time=0, tempo=self.tempo_bpm)

        for i in range(len(instruments)):
            # todo: get actual track names from project file (or are they stored in instrument files?)
            midi_file.addTrackName(track=0, time=0, trackName=f"Instrument {instruments[i]}")

            instrument_to_midi_track_map[instruments[i]] = i

        for track in self.pattern.tracks:

            for step_number in range(track.length):

                step = track.steps[step_number]

                if step.note.is_empty():
                    continue

                if step.note.is_off_fad_or_cut():
                    # this is a hack as midi utils try to set note off events automatically
                    try:
                        note_to_disable = last_processed_step_by_instrument[step.instrument_number].note
                    except KeyError:
                        # note off events in tracker can be before actual note
                        # this is typically useful for arrangement of several
                        # sequential patterns
                        # FIXME: handle this case when implementing rendering of a song with several patterns
                        pass
                    else:

                        midi_track_number = instrument_to_midi_track_map[step.instrument_number]
                        if midi_file.header.numeric_format == 1:
                            midi_track_number += 1
                        midi_track = midi_file.tracks[midi_track_number]

                        midi_track.eventList.append(
                            NoteOff(channel=channel,
                                    pitch=PatternToMidiExporter.get_midi_note_value(note_to_disable),
                                    tick=midi_file.time_to_ticks(step_number*PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE),
                                    # fixme: should volume be the same as of note from last step?
                                    volume=default_volume
                                    )
                        )

                else:

                    # we've got a note
                    # TODO: add support for chord fx
                    # TODO: add support for arp fx
                    midi_file.addNote(track=instrument_to_midi_track_map[step.instrument_number],
                                      channel=channel,
                                      pitch=PatternToMidiExporter.get_midi_note_value(step.note),
                                      time=step_number*PatternToMidiExporter.MIDI_16TH_NOTE_TIME_VALUE,
                                      duration=default_duration,   # does not matter as we will delete note off event,
                                      # TODO: write velocity fx value if set (needs to be converted to 0...127!!!)
                                      volume=default_volume,
                                      )

                    # delete note off event as we add it ourselves
                    # (this is not documented, but seems to be a safe way to do it)
                    midi_track_number = instrument_to_midi_track_map[step.instrument_number]
                    if midi_file.header.numeric_format == 1:
                        midi_track_number += 1
                    midi_track = midi_file.tracks[midi_track_number]
                    midi_track.eventList.pop()

                    # add this so we can handle note off events properly
                    # as they require you to tell which note you would
                    # like to stop playing
                    last_processed_step_by_instrument[step.instrument_number]=step

                    # fixme: should we add note off at the last step for all instruments?



        # for i, pitch in enumerate(degrees):
        #     midi_file.addNote(track, channel, pitch, time + i, default_duration, default_volume)

        return midi_file

    def write_midi_file(self, path: str):

        midi_file = self.generate_midi()

        with open(path, "wb") as output_file:
            midi_file.writeFile(output_file)



