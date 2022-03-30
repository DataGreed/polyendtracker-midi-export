# TODO: enums for fx types
import math
from enum import Enum
from typing import List, Union

__author__ = "Alexey 'DataGreed' Strelkov"

class EffectType(Enum):
    volume = 0x12
    panning = 0x1F
    chord = 0xE  # dec 14
    arp = 0x15   # dec 21    # arpeggio works only with chord fx at the same step

    # todo: add all effect types

    def short_name(self):
        try:
            return EFFECT_SHORT_NAMES[self.value]
        except AttributeError:
            return EFFECT_SHORT_NAMES[self]


# short names the way they are represented in tracker UI
EFFECT_SHORT_NAMES = {
    EffectType.volume.value: "V",
    EffectType.panning.value: "P",
    EffectType.chord.value: "Ch",
    EffectType.arp.value: "Ar",
    # todo: add all effect types
}


class Effect:
    def __init__(self, fx_type: Union[int, EffectType], fx_value: int):

        self.type = fx_type  # todo: ditch this ambiguous field. Use type_value and type_obj instead
        self.value = fx_value

        # declare type_value and type_obj depending on the type of fx_type
        # (it can be value from tracker pattern file or actual EffectType enum value)
        if isinstance(fx_type, int):

            self.type_value = fx_type
            try:
                self.type_obj = EffectType(self.type_value)
            except ValueError as e:
                # that's okay for now as we don't have all of the fx types described
                # todo: describe all effect types in EffectType enum
                self.type_obj = None

        elif isinstance(fx_type, EffectType):
            self.type_obj = fx_type
            self.type_value = fx_type.value

        else:
            raise ValueError(f"fx_type must be int or EffectType, got {type(fx_type)} instead")

        # todo: write down all effect types in a enum and check range of values for each of them
        #  so we we can have a human-readable version.
        # todo: ditch the Union[int, EffectType] when all effects will be described and separate
        # effect type value and actual object type in different variable

    def get_name(self):
        try:
            return EffectType.short_name(self.type)
        except KeyError:
            # for effects that has not been yet mapped out and for future compatibility
            # in case new effects will be added
            return str(self.type)

    def get_chord_type(self):
        if self.type_obj == EffectType.chord and self.value:
            from . import chords
            chord_type = chords.ChordType.get_by_fx_value(self.value)

            return chord_type
        return None

    def get_arp_type(self):
        if self.type_obj == EffectType.arp and self.value:
            from . import arps
            arp_type = arps.ArpType.get_by_fx_value(self.value)

            return arp_type
        return None

    def get_value_display(self):

        # handle special cases for rendering values
        if self.type_obj == EffectType.chord:
            # print("ENCOUNTERED CHORD")
            if self.value:
                chord_type = self.get_chord_type()
                return chord_type.render()

        elif self.type_obj == EffectType.arp:
            if self.value:
                arp_type = self.get_arp_type()
                return arp_type.render()

        return self.value

    def render(self, hide_value_if_no_type_set=True):
        # tracker stores fx values even for deleted effects.
        # TODO: use names when we have all effect names mapped out in EffectType enum
        return f"{self.get_name() if self.type else '--'}".rjust(3) + f"{self.get_value_display() if self.type else '---'}".rjust(4)

    def __str__(self):

        return self.render(hide_value_if_no_type_set=False)



class Note:

    OFF_VALUE = 0xFC
    CUT_VALUE = 0xFD
    FADE_VALUE = 0xFE

    EMPTY_VALUE = 0xFF

    INAUDIBLE_VALUES = (OFF_VALUE, CUT_VALUE, FADE_VALUE, EMPTY_VALUE)
    NOTE_DISABLING_VALUES = (OFF_VALUE, CUT_VALUE, FADE_VALUE)

    # note names in the order they appear in octave in notation
    NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def __init__(self, value: int):
        self.value = value

        self.octave = math.floor(value/12)
        self.name = Note.NOTE_NAMES[value % 12]

        # special cases
        if value == Note.EMPTY_VALUE:
            self.name = "---"
        elif value == Note.OFF_VALUE:
            self.name = "OFF"
        elif value == Note.FADE_VALUE:
            self.name = "FAD"
        elif value == Note.CUT_VALUE:
            self.name = "CUT"

    def is_empty(self):

        return self.value == Note.EMPTY_VALUE

    def is_off_fad_or_cut(self):
        return self.value in Note.NOTE_DISABLING_VALUES

    def __str__(self):
        if self.value in Note.INAUDIBLE_VALUES:
            return self.name
        return f"{self.name}{self.octave}"


class Step:

    # payload length in bytes
    PAYLOAD_LENGTH = 6

    NOTE_OFFSET = 0
    INSTRUMENT_OFFSET = 1

    FX2_TYPE_OFFSET = 2
    FX2_VALUE_OFFSET = 3

    FX1_TYPE_OFFSET = 4
    FX1_VALUE_OFFSET = 5

    def __init__(self, note:Note, instrument_number:int, fx1: Effect, fx2: Effect):

        self.note = note
        self.instrument_number = instrument_number
        self.fx1 = fx1
        self.fx2 = fx2

    def __str__(self):

        # todo: make sure this string has constant length so we can print pretty tables
        return f"{self.note} inst {self.instrument_number} fx1 {self.fx1} fx2 {self.fx2}"

    def render_as_table_cell(self):

        return f"{self.note}".rjust(3) +f"{self.instrument_number or '--'}".rjust(3) + f"{self.fx1} {self.fx2}"

    @staticmethod
    def from_bytes(data: bytes):

        if len(data) != Step.PAYLOAD_LENGTH:
            raise ValueError(f"Expected Step payload to be {Step.PAYLOAD_LENGTH} bytes long, got {len(bytes)} instead")

        return Step(note=Note(data[Step.NOTE_OFFSET]),
                    instrument_number=data[Step.INSTRUMENT_OFFSET],
                    fx1=Effect(fx_type=data[Step.FX1_TYPE_OFFSET], fx_value=data[Step.FX1_VALUE_OFFSET]),
                    fx2=Effect(fx_type=data[Step.FX2_TYPE_OFFSET], fx_value=data[Step.FX2_VALUE_OFFSET]))

    def get_chord(self):
        """
        Returns chord of this step has chord fx. Returns None if not.
        If step has 2 chord effects, returns the first one
        (this case should not be valid - not sure how tracker even handles this)
        """

        chord_type = self.fx1.get_chord_type() or self.fx2.get_chord_type()
        if chord_type:
            return chord_type.get_chord(self.note)
        return None

    def get_arp(self):
        """
        Returns arp if this step has arp fx at any effect slot. Returns None if not.
        Note: this will return arp only if
        the same step has chord fx (because arp fx doesn't make sense without chord fx
        and just won't work without chord fx set on the same step really).

        Arp needs chord to be initialized, so it can't be returned without chord anyway
        :return:
        """
        arp_type = self.fx1.get_arp_type() or self.fx2.get_arp_type()
        if arp_type:
            chord = self.get_chord()
            if not chord:
                return None
            return arp_type.get_arp(chord)
        return None


class Track:

    # track payload length in bytes
    PAYLOAD_LENGTH = 769
    # number of sequencer steps in tracks (1/16 steps)
    NUMBER_OF_STEPS = 128

    def __init__(self, length: int, steps: List[Step]):
        self.length = length
        self.steps = steps

        if len(steps) != 128:
            raise ValueError(f"Track must have 128 steps, only {len(steps)} passed")

        if length > 128 or length < 1:
            raise ValueError(f"Track length must be in 1...128 range. {length} passed instead")

    def __str__(self):
        return " | ".join([str(x) for x in self.steps])

    @staticmethod
    def from_bytes(data: bytes):

        if len(data) != Track.PAYLOAD_LENGTH:
            raise ValueError(f"Expected track payload {Track.PAYLOAD_LENGTH} bytes long, got {len(data)} instead")

        pattern_length = data[0] + 1  # pattern length is zero-based, actual lowest length is 1

        # remove pattern length for easier iteration
        steps_data = data[1:]

        steps = []

        # sanity check
        if len(steps_data)/Track.NUMBER_OF_STEPS != Step.PAYLOAD_LENGTH:
            raise ValueError("Internal Error: track payload does not divide by number of steps as expected")

        for i in range(Track.NUMBER_OF_STEPS):
            start_offset = i * Step.PAYLOAD_LENGTH
            end_offset = (i + 1) * Step.PAYLOAD_LENGTH

            steps.append(Step.from_bytes(steps_data[start_offset:end_offset]))

        return Track(length=pattern_length, steps=steps)


class Pattern:

    OFFSET_START = 0x1c
    OFFSET_END = 0x1824
    NUMBER_OF_TRACKS = 8

    def __init__(self, tracks: List[Track]):
        self.tracks = tracks

        if len(tracks) != Pattern.NUMBER_OF_TRACKS:
            raise ValueError(f"Pattern must have {Pattern.NUMBER_OF_TRACKS} tracks, got only {len(tracks)}")

    def __str__(self):
        # TODO: add vertical printing option for easy comparision with actual tracker output
        result = ""
        i = 1
        for track in self.tracks:
            result += f"Track {i}: {track}\n"
            i+=1

        return result

    def render_as_table(self):
        """
        Prints pattern tracks vertically in a similar
        way the actual tracker does it
        :return:
        """
        result = []

        header_items = [f"Track {x+1}".center(21) for x in range(Pattern.NUMBER_OF_TRACKS)]
        result.append(" | ".join(header_items) + " ")

        for i in range(self.tracks[0].length):  # all track lengths are the same as of firmware 1.5
            line_data = []
            for track in self.tracks:
                line_data.append(str(track.steps[i].render_as_table_cell()))

            result.append(" | ".join(line_data) + " ")

        return str("\n".join(result))


    @staticmethod
    def from_bytes(data: bytes):

        expected_length = Pattern.OFFSET_END - Pattern.OFFSET_START # 6152 or 769*8 just for sanity check

        if len(data) != expected_length:
            raise ValueError(f"Expected pattern data {expected_length} bytes long, got {len(data)} instead")

        # sanity check
        if len(data) / Track.PAYLOAD_LENGTH != Pattern.NUMBER_OF_TRACKS:
            raise ValueError(f"Internal Error: Tracks payload length does not divide by {Pattern.NUMBER_OF_TRACKS}.")

        tracks = []

        for i in range(Pattern.NUMBER_OF_TRACKS):

            start_offset = i*Track.PAYLOAD_LENGTH
            end_offset = (i+1)*Track.PAYLOAD_LENGTH

            tracks.append(Track.from_bytes(data[start_offset:end_offset]))

        return Pattern(tracks=tracks)


class PatternParser:
    """
    Parser for Polyend Tracker pattern *.mtp filtes
    """
    def __init__(self, filename: str):

        self.filename = filename

    def parse(self) -> Pattern:
        with open(self.filename, "rb") as f:

            return Pattern.from_bytes(f.read()[Pattern.OFFSET_START:Pattern.OFFSET_END])
