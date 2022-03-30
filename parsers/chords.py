from copy import deepcopy
from typing import List

from parsers.patterns import Note


class Chord:
    # represents a chord, a collection of notes that
    # is generated from a step with a chord effect
    # enabled on it

    # fixme: it troubles me a little that this class is a little backwards:
    #  it takes notes and intervals in constructor instead of step fx chord value
    #  which would probably make more sense still we are using this class for parsing
    #  and not for constructing something

    def __init__(self, root_note: Note, intervals: List[int]):
        """
        Creates a chord from root note and intervals
        :param root_note: the root note of the chords
        :param intervals: a list of integers with all the semitone intervals above the note
        that have to be played, this must include a root note (0) if you want it to be played,
        e.g. [0, 4, 7] plays a major chord; [0, 3, 7] plays a minor chord
        """
        self.root_note: Note = root_note
        self.intervals: List[int] = intervals

        # todo: handle cases with empty values (off, cut, fad)

    @property
    def notes(self) -> List[Note]:
        """
        :return: an array of Note objects to be played as a chord
        """
        # todo: handle cases with empty values (off, cut, fad)
        result = []
        for interval in self.intervals:
            if interval == 0:
                result.append(self.root_note)
            else:
                # note values are represented as semitones in tracker,
                # so we can just directly add interval to the value
                # to get note within the interval
                result.append(Note(value=self.root_note.value+interval))
        return result

    @property
    def fx_value(self) -> int:
        try:
            return CHORD_TYPES_BY_INTERVAL_TUPLE[tuple(self.intervals)].value
        except KeyError as e:
            raise ValueError(f"ChordType with intervals {tuple(self.intervals)} "
                             f"not found in SUPPORTED_CHORDS. "
                             f"Original exception follows: {e}")

    @property
    def chord_type(self) -> "ChordType":
        try:
            return CHORD_TYPES_BY_INTERVAL_TUPLE[tuple(self.intervals)]
        except KeyError as e:
            raise ValueError(f"ChordType with intervals {tuple(self.intervals)} "
                             f"not found in SUPPORTED_CHORDS. "
                             f"Original exception follows: {e}")

    @classmethod
    def create_from_fx_value(cls, root_note:Note, fx_value: int) -> "Chord":
        """
        Creates a chord object from the actual value
        stored in a step of tracker pattern file (*.mtp)
        :param fx_value: value of chord fx from tracker pattern file
        :param root_note: Note object, root (base) note of the chord
        :return:
        """
        return CHORD_TYPES_BY_VALUE[fx_value].get_chord(root_note=root_note)

    def __str__(self):
        return f"{self.root_note} {self.fx_value}"


class ChordType:

    def __init__(self, display_name: str, verbose_name: str, value: int, intervals: List[int]):
        self.display_name = display_name
        self.verbose_name = verbose_name
        self.value = value
        self.intervals = intervals

    def get_chord(self, root_note: Note) -> Chord:
        """
        Constructs a Chord object for given root note
        """
        return Chord(root_note=root_note, intervals=self.intervals)

    # @classmethod
    # def create_from_fx_value(cls, fx_value: int):
    #     return deepcopy(CHORD_TYPES_BY_VALUE[fx_value])

    @classmethod
    def get_by_fx_value(cls, fx_value: int) -> "ChordType":
        return CHORD_TYPES_BY_VALUE[fx_value]

    def __str__(self):
        return self.render()

    def render(self):
        return f"{self.display_name}"


SUPPORTED_CHORD_TYPES = [
    # todo: handle disabled chord with value 0 somehow

    # Sus2 – 027
    ChordType("27", "Sus2", 1, [0, 2, 7]),
    # Sus2 #5 – 028
    ChordType("28", "Sus2 #5", 2, [0, 2, 8]),
    # DimTriad – 036
    ChordType("36", "DimTriad", 3, [0, 3, 6]),
    # Min – 037
    ChordType("37", "Min", 4, [0, 3, 7]),
    # Maj – 047
    ChordType("47", "Maj", 5, [0, 4, 7]),
    # AugTriad – 048
    ChordType("48", "AugTriad", 6, [0, 4, 8]),
    # Sus4 – 057
    ChordType("57", "Sus4", 7, [0, 5, 7]),

    # Stack4 – 05A - modal quant chord? not quite sure
    # todo: make sure that intervals are correct
    ChordType("5A", "Stack4", 8, [0, 5, 10]),   # does tracker send 3 notes or 4? 4th would be 15

    # Open4 – 05C
    # todo: do they mean perfect 4th? or is it something else?
    ChordType("5C", "Open4", 9, [0, 5]),

    # Sus #4 – 067
    ChordType("67", "Sus #4", 10, [0, 6, 7]),

    # Open5 – 07C
    # todo: do they mean power chord? or is it something else
    ChordType("07C", "Open5", 11, [0, 7]),

    # Stack5 – 07E
    # todo: make sure that intervals are correct
    ChordType("07", "Stack5", 12, [0, 7, 14]),

    # Sus2add6 – 0279
    ChordType("279", "Sus2add6", 13, [0, 2, 7, 9]),

    # Sus2 b7 – 027A
    # todo: make sure intervals are correct, they were deduced
    ChordType("27A", "Sus2 b7", 14, [0, 2, 7, 10]),

    # Sus2Maj7 – 027B
    # todo: make sure intervals are correct, they were deduced
    ChordType("27B", "Sus2Maj7", 15, [0, 2, 7, 11]),

    # Dim7 – 0369
    ChordType("369", "Dim7", 16, [0, 3, 6, 9]),

    # HalfDim – 036A
    # see https://en.wikipedia.org/wiki/Half-diminished_seventh_chord
    ChordType("36A", "HalfDim", 17, [0, 3, 6, 10]),

    # Min b6 – 0378
    ChordType("378", "Min b6", 18, [0, 3, 7, 8]),
    # Min6 – 0379
    ChordType("379", "Min6", 19, [0, 3, 7, 9]),

    # Min7 – 037A
    # see https://en.wikipedia.org/wiki/Minor_seventh_chord
    ChordType("37A", "Min7", 20, [0, 3, 7, 10]),

    # MinMaj7 – 037B
    # see https://en.wikipedia.org/wiki/Minor_major_seventh_chord
    ChordType("37B", "MinMaj7", 21, [0, 3, 7, 11]),

    # Maj6 – 0479
    ChordType("479", "Maj6", 22, [0, 4, 7, 9]),

    # Dom7 – 047A
    # see https://en.wikipedia.org/wiki/Dominant_seventh_chord
    ChordType("47A", "Dom7", 23, [0, 4, 7, 10]),

    # Maj7 – 047B
    # see https://en.wikipedia.org/wiki/Major_seventh_chord
    ChordType("47B", "Maj7", 24, [0, 4, 7, 11]),

    # Aug add6 – 0489
    ChordType("489", "Aug add6", 25, [0, 4, 8, 9]),

    # Aug b7 – 048A
    # todo: make sure this is correct, as the intervals are deduced from chord name
    ChordType("48A", "Aug b7", 26, [0, 4, 8, 10]),

    # AugMaj7 – 048B
    # see https://en.wikipedia.org/wiki/Augmented_major_seventh_chord
    ChordType("48B", "AugMaj7", 27, [0, 4, 8, 11]),

    # Sus4 b7 – 057A
    # todo: make sure this is correct, I am not sure about the last interval
    ChordType("57A", "Sus4 b7", 28, [0, 5, 7, 10]),

    # Sus4Maj7 – 057B
    # todo: make sure this is correct, I am not sure about the last interval
    ChordType("57B", "Sus4Maj7", 29, [0, 5, 7, 11]),   # todo: add chord values
]
# mapping tracker value: chord object
CHORD_TYPES_BY_VALUE = {item.value: item for item in SUPPORTED_CHORD_TYPES}

# chord mapping by interval tuple (tuple, not list, as lists are not hashable)
CHORD_TYPES_BY_INTERVAL_TUPLE = {tuple(item.intervals): item for item in SUPPORTED_CHORD_TYPES}
