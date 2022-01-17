
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

    @staticmethod
    def from_bytes(data):
        raise NotImplementedError()


class Note:

    # note names in the order they appear in octave in notation
    NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "G", "G#", "A", "A#", "B")

    def __init__(self, value: int):
        self.value = value

        self.octave = math.floor(value/12)
        self.name = Note.NOTE_NAMES[value % 12]

    def __str__(self):
        return f"{self.name}{self.octave}"

    @staticmethod
    def from_bytes(data):
        raise NotImplementedError()


class Step:

    def _init__(self, note:Note, instrument_number:int, fx1: Effect, fx2: Effect):

        self.note = note
        self.instrument_number = instrument_number
        self.fx1 = fx1
        self.fx2 = fx2

    def __str__(self):

        # todo: make sure this string has constant length
        return f"{self.note} inst {self.instrument_number} fx1 {self.fx1} fx2 {self.fx2}"

    @staticmethod
    def from_bytes(data):
        raise NotImplementedError()


class Track:

    # track payload length in bytes
    PAYLOAD_LENGTH = 769

    def __init__(self, length: int, steps: List[Step]):
        self.length = length
        self.steps = steps

        if len(steps) != 128:
            raise ValueError(f"Track must have 128 steps, only {len(steps)} passed")

        if length > 128 or length < 1:
            raise ValueError(f"Track length must be in 1...128 range. {length} passed instead")

    @staticmethod
    def from_bytes(data:bytes):
        expected_length = 8*769
        if len(bytes) != expected_length:
            raise ValueError(f"Expected tracks payload {expected_length} bytes long, got {len(data)} instead")

        raise NotImplementedError()


class Pattern:

    OFFSET_START = 0x1c
    OFFSET_END = 0x1824

    def __init__(self, tracks: List[Track]):
        self.tracks = tracks

        if len(tracks) != 8:
            raise ValueError(f"Pattern must have 8 tracks, got only {len(tracks)}")

    @staticmethod
    def from_bytes(data: bytes):

        expected_length = Pattern.OFFSET_END - Pattern.OFFSET_START # 6152 just for sanity check

        if len(data) != expected_length:
            raise ValueError(f"Expected pattern data {expected_length} bytes long, got {len(data)} instead")

        #

        raise NotImplementedError()


class PatternParser:

    def __init__(self, filename: str):

        self.filename = filename

    def parse(self) -> Pattern:
        with open(self.filename, "rb") as f:

            return Pattern.from_bytes(f.read())
