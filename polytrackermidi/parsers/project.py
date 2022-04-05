# polyend tracker project file

__author__ = "Alexey 'DataGreed' Strelkov"

import os
import struct
from typing import List, Dict

from polytrackermidi.parsers.patterns import Pattern


class Song:
    """
    Represents a song, a sequence of patterns
    """

    """Maximum length of a song in patterns."""
    MAXIMUM_SLOTS_PER_SONG = 255  # from docs

    def __init__(self, pattern_chain: List[int], pattern_mapping: Dict[int, Pattern],
                 bpm:float):
        """

        :param pattern_chain: a list of ints representing the order of patterns in the song.
         ints a 1-based. So pattern 1 is represented by 1.
        :param pattern_mapping:   a dict with all of the unique patterns in the song.
        Keys are integer number of patterns, values are actual patterns.
        """
        self.bpm = bpm
        if len(pattern_chain)>self.MAXIMUM_SLOTS_PER_SONG:
            raise ValueError(f"Maximum song length is {self.MAXIMUM_SLOTS_PER_SONG}, "
                             f"but {len(pattern_chain)} pattern long song received")
        self.pattern_mapping = pattern_mapping
        self.pattern_chain = pattern_chain

        # integrity check
        for i in set(pattern_chain):
            if i not in pattern_mapping.keys():
                raise ValueError(f"Song initialization: pattern_chain has value "
                                 f"{i}, but there is no such pattern in pattern_mapping. "
                                 f"Context: pattern_chain: {pattern_chain}; "
                                 f"pattern_mapping: {pattern_mapping}")

    def get_song_as_patterns(self) -> List[Pattern]:
        """Returns song as a list of patterns ordered. Play them in
        the returned order to get the song"""
        return [self.pattern_mapping[x] for x in self.pattern_chain]


class Project:
    """
    Represents a tracker project
    """

    def __init__(self, name: str, song: Song):
        """
        :param name: name of the project
        :param bpm: project tempo in beats per minutes. Tracker supports fractional tempo
        :param song: song (sequence of patterns to play)
        """
        self.name = name
        self.song = song

    OFFSET_END = 0x624 #1572 bytes total files length
    OFFSET_START = 0

    PATTERN_CHAIN_OFFSET = 0x10
    PATTERN_CHAIN_END = 0x10f   # length is 255 bytes

    BPM_OFFSET_START = 0x1c0
    BPM_BYTES_LENGTH = 4    # it's a 32bit float. The 40-800 and limit and 0.1 precision are artificial

    @staticmethod
    def from_bytes(data: bytes, patterns_bytes=Dict[int,bytes]) -> "Project":
        """
        Constructs a project object from bytes extracted from project file.
        :param data:
        :param patterns_bytes: a list of bytes for each of projects
        patterns extracted from pattern files. Note: expects full file
        byte representation without offsets.
        :return:
        """
        expected_length = Project.OFFSET_END - Project.OFFSET_START  # 6152 or 769*8 just for sanity check

        if len(data) != expected_length:
            raise ValueError(f"Expected project data {expected_length} bytes long, got {len(data)} instead")

        patterns_mapping = {}

        # parse patterns from received bytes for each pattern file
        # and save them in a dict tha maps pattern number to Pattern object
        # so it can be used later to construct a song
        for key, value in patterns_bytes.items():
            patterns_mapping[key] = Pattern.from_bytes(value[Pattern.OFFSET_START:Pattern.OFFSET_END])

        bpm = Project.bpm_from_bytes(data[Project.BPM_OFFSET_START:Project.BPM_OFFSET_START+Project.BPM_BYTES_LENGTH])

        pattern_chain = Project.pattern_chain_from_bytes(data[Project.PATTERN_CHAIN_OFFSET:Project.PATTERN_CHAIN_END])

        # todo: extract from project files footer
        # tracker project files actually store file names inside of them, but
        # the problem is that it seems to be buggy, since a lot of times i see
        # part of the previous project names in new projects with shorter names.
        # not sure if it's actually possible to unpack a real, not mangled name
        # from a project file.
        name = "MyProject"

        return Project(name=name,
                       song=Song(pattern_chain=pattern_chain,
                                 pattern_mapping=patterns_mapping,
                                 bpm=bpm),
                       )

    @staticmethod
    def pattern_chain_from_bytes(data: bytes) -> List[int]:
        """extracts chain of patterns for song from project file bytes"""

        # print("EXTRACTING pattern chain from sequence of bytes below:")
        # print(data)
        # print(f"data length {len(data)}")

        result = []

        for byte in data:
            # each byte is just a pattern number
            # print(byte)
            if byte:
                result.append(byte)
            else:
                # break when we encounter zero. It stand for unoccupied slot.
                # there could be no unoccupied slots in a sond (I guess?)
                # todo: check that it's correct
                break

        return result

    @staticmethod
    def bpm_from_bytes(data: bytes) -> List[int]:

        if len(data) != 4:
            raise ValueError(f"Length of data for BPM should be 4 bytes, but received {len(bytes)}: {bytes}")
        # unpacks 4 bytes to a float
        return round(struct.unpack('f', data)[0], 1)



class ProjectParser:
    """Parses tracker *.mt files, scans directory for patterns
    so a song can be exported to MIDI"""

    PATTERNS_FOLDER_NAME = "patterns"
    DEFAULT_PROJECT_FILENAME = "project.mt"
    PATTERN_FILE_NAME_TEMPLATE = "pattern_{}.mtp"   # todo: format: add leading zero automatically

    MAXIMUM_PATTERNS_PER_PROJECT = 255  # from polyend docs

    def __init__(self, filename_or_folder: str):
        """
        :param filename_or_folder: project (*.mt) filename or folder with project file.
        Note that pattern files are required to be in a "patterns" subfolder within
        the same folder for everything to work properly.
        """
        if filename_or_folder.endswith(".mt"):
            self.filepath = filename_or_folder
            # folder must always end with a folder separator
            self.folder = os.sep.join(filename_or_folder.split(os.sep)[:-1]) + os.sep
        else:
            self.folder = filename_or_folder
            if not self.folder.endswith(os.sep):
                # folder must always end with a folder separator
                self.folder += os.sep
            self.filepath = self.folder+self.DEFAULT_PROJECT_FILENAME

        self.patterns_folder = self.folder + self.PATTERNS_FOLDER_NAME + os.sep

    def parse(self) -> Project:

        project_file_bytes = None
        pattern_file_bytes_dict: Dict[int, bytes] = {}

        with open(self.filepath, "rb") as f:
            project_file_bytes = f.read()  # f.read()[Project.OFFSET_START:Project.OFFSET_END]

        # find all project pattern files and add their bytes to the parser too
        for i in range(1, self.MAXIMUM_PATTERNS_PER_PROJECT+1):
            pattern_file_path = self.patterns_folder+self.PATTERN_FILE_NAME_TEMPLATE

            # FIXME: patterns names goe as pattern_01.mtp, but manual says there can be
            #  255 patterns, how pattern 100 file will be named if
            #  there is only 1 leading zero in one digit projects?

            pattern_number_string = str(i)
            if len(pattern_number_string) < 2:
                pattern_number_string = "0" + pattern_number_string

            pattern_file_path = pattern_file_path.replace("{}", pattern_number_string)

            try:
                with open(pattern_file_path, "rb") as f:
                    # pattern
                    pattern_file_bytes_dict[i] = f.read()   # reads the whole file
            except FileNotFoundError as e:
                # it's okay. Not all patterns have to exist.
                pass

        return Project.from_bytes(project_file_bytes, pattern_file_bytes_dict)
