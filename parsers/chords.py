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

        pass

    @classmethod
    def create_from_fx_value(cls, note:Note, fx_value: int):
        """
        Creates a chord object from the actual value
        stored in a step of tracker pattern file (*.mtp)
        :param chord_fx_value:
        :return:
        """
        raise NotImplementedError('not yet implemented')
        pass



class ChordType:

    def __init__(self, display_name: str, verbose_name: str, value: int, intervals: List[int]):
        self.display_name = display_name
        self.verbose_name = verbose_name
        self.value = value
        self.intervals = intervals

    def get_chord(self, root_note: Note):
        """
        Constructs a Chord object for given root note
        """
        return Chord(root_note=root_note, intervals=self.intervals)


SUPPORTED_CHORD_TYPES = [
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
    # Stack4 – 05A
    ChordType("", "", 8, []),   # todo: add chord values
    # Open4 – 05C
    ChordType("", "", 9, []),   # todo: add chord values
    #Sus #4 – 067
    ChordType("67", "Sus #4", 10, [0, 6, 7]),
    # Open5 – 07C
    ChordType("", "", 11, []),   # todo: add chord values
    # Stack5 – 07E
    ChordType("", "", 12, []),   # todo: add chord values
    # Sus2add6 – 0279
    ChordType("279", "Sus2add6", 13, [0, 2, 7, 9]),
    # Sus2 b7 – 027A
    ChordType("", "", 14, []),   # todo: add chord values
    # Sus2Maj7 – 027B
    ChordType("", "", 15, []),   # todo: add chord values
    # Dim7 – 0369
    ChordType("369", "Dim7", 16, [0, 3, 6, 9]),
    # HalfDim – 036A
    ChordType("", "", 17, []),   # todo: add chord values
    # Min b6 – 0378
    ChordType("378", "Min b6", 18, [0, 3, 7, 8]),
    # Min6 – 0379
    ChordType("379", "Min6", 19, [0, 3, 7, 9]),
    # Min7 – 037A
    ChordType("", "", 20, []),   # todo: add chord values
    # MinMaj7 – 037B
    ChordType("", "", 21, []),   # todo: add chord values
    # Maj6 – 0479
    ChordType("479", "Maj6", 22, [0, 4, 7, 9]),
    # Dom7 – 047A
    ChordType("", "", 23, []),   # todo: add chord values
    # Maj7 – 047B
    ChordType("", "", 24, []),   # todo: add chord values
    # Aug add6 – 0489
    ChordType("489", "Aug add6", 25, [0, 4, 8, 9]),
    # Aug b7 – 048A
    ChordType("", "", 26, []),   # todo: add chord values
    # AugMaj7 – 048B
    ChordType("", "", 27, []),   # todo: add chord values
    # Sus4 b7 – 057A
    ChordType("", "", 28, []),   # todo: add chord values
    # Sus4Maj7 – 057B
    ChordType("", "", 29, []),   # todo: add chord values
]
# todo: map via comprehension
# CHORD_TYPES_BY_VALUE
# CHORD_TYPES_BY_DISPLAY_NAME

