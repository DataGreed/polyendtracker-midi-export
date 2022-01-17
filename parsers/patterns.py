
# TODO: enums for fx types
import math
from enum import Enum
from typing import List


class EffectType(Enum):
    volume = 0x12
    panning = 0x1F
    # todo: add all effect types

    def short_name(self):
        return EFFECT_SHORT_NAMES[self]


# short names the way they are represented in tracker UI
EFFECT_SHORT_NAMES = {
    EffectType.volume: "V",
    EffectType.panning: "P",
    # todo: add all effect types
}


class Effect:
    def __init__(self, fx_type: int, fx_value: int):
        self.type = fx_type
        self.value = fx_value

        # todo: write down all effect types in a enum and check range of values for each of them
        #  so we we can have a human-readable version

    def __str__(self):
        return f"{self.type} {self.value}"



class Note:

    OFF_VALUE = 0xFC
    CUT_VALUE = 0xFD
    FADE_VALUE = 0xFE

    EMPTY_VALUE = 0xFF

    INAUDIBLE_VALUES = (OFF_VALUE, CUT_VALUE, FADE_VALUE, EMPTY_VALUE)

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

    @staticmethod
    def from_bytes(data: bytes):

        if len(data) != Step.PAYLOAD_LENGTH:
            raise ValueError(f"Expected Step payload to be {Step.PAYLOAD_LENGTH} bytes long, got {len(bytes)} instead")

        return Step(note=Note(data[Step.NOTE_OFFSET]),
                    instrument_number=data[Step.INSTRUMENT_OFFSET],
                    fx1=Effect(fx_type=data[Step.FX1_TYPE_OFFSET], fx_value=data[Step.FX1_VALUE_OFFSET]),
                    fx2=Effect(fx_type=data[Step.FX2_TYPE_OFFSET], fx_value=data[Step.FX2_VALUE_OFFSET]))


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

    def __init__(self, filename: str):

        self.filename = filename

    def parse(self) -> Pattern:
        with open(self.filename, "rb") as f:

            return Pattern.from_bytes(f.read()[Pattern.OFFSET_START:Pattern.OFFSET_END])
