import itertools
import random
from enum import Enum

from polytrackermidi.parsers.chords import Chord

class ArpDirection(Enum):
    raising = 1
    falling = -1
    random = 0

class EndlessRandomIterator(object):
    """
    Iterates endlessly on a provided list,
    returning random values from it each time
    """
    def __init__(self, iterable:list):
        self.iterable = iterable
        if not iterable:
            raise ValueError

    def __iter__(self):
        return self

    def __next__(self):
        return random.choice(self.iterable)
        # raise StopIteration

class Arp:
    def __init__(self, chord: Chord, direction: ArpDirection, division: float):
        self.division = division
        self.direction = direction
        self.chord = chord

    def get_notes_iterator(self):
        """
        Creates new endless iterator over chord
        notes in the direction of arpeggiation.
        Can be used to iterate over playable
        notes to play arpeggio.
        Returns new iterator everytime so it's
        possible to retrigger arp.
        """
        if self.direction == ArpDirection.raising:
            return itertools.cycle(self.chord.notes)
        elif self.direction == ArpDirection.falling:
            return itertools.cycle(reversed(self.chord.notes))
        elif self.direction == ArpDirection.random:
            # I have no idea what kind of algo tracker implements - they could probably
            # always generate different notes to avoid placing two same notes in a row (or not)
            return EndlessRandomIterator(self.chord.notes)

        else:
            raise ValueError(f"Unsupported arp direction: {self.direction}")


class ArpType:
    """
    Represents arpeggiation type that can be initialized
    from arp fx value of the tracker pattern (*.mtp) file
    """

    def __init__(self, display_name: str, verbose_name: str = "", value: int = 0,
                 direction: ArpDirection = None,
                 division: float = 0, try_deduct_from_name: bool = True):
        """
        :param display_name: name that is displayed in tracker interface
        :param verbose_name: human readable name
        :param value: value that this type of arp is saved as withing tracker pattern file
        :param direction: direction of arpeggiation
        :param division: how many steps (1/16 notes) it takes for next note to play. 1 means that
                         it plays every step. Can be fractional! Goes as low as 1/8 of a step
                         (basically (1/16)/8 - not even sure why tracker allows such small divisions)
                         1/8 of a step is displayed as .8 in tracker interface.
                         1/2 of a step displayed as .2 in tracker UI
        :param try_deduct_from_name:
        """
        self.value = value
        self.verbose_name = verbose_name
        self.direction = direction
        self.division = division
        self.display_name = display_name

        if (not direction or not division) and try_deduct_from_name:
            self._initialize_from_name(display_name=display_name)

    def _initialize_from_name(self, display_name: str):
        """deduces arp type parameters from display name
        because as a programmer I am lazy not willing to list
        all parameters manually :P"""
        display_name = display_name.strip()
        direction_char = display_name[0]

        if direction_char == "/":
            self.direction = ArpDirection.raising
        elif direction_char == "\\":
            self.direction = ArpDirection.falling
        elif direction_char.lower() == "r":
            self.direction = ArpDirection.random
        else:
            raise ValueError(f"unknown arp direction character: '{direction_char}' ({display_name})")

        division_char = display_name.strip()[-1]
        try:
            division_int = int(division_char)
        except ValueError:
            raise ValueError(f"unknown arp division character: '{division_char}'  ({display_name})")

        if "." in display_name:
            self.division = 1/division_int
        else:
            self.division = division_int

        # not really needed, added for being inline with chord classes
        self.verbose_name = self.display_name

    def render(self):
        return self.display_name

    def __str__(self):
        return self.render()

    def get_arp(self, chord: Chord) -> Arp:
        """
        Returns an Arp object for given chord
        """
        return Arp(chord=chord, direction=self.direction, division=self.division)

    # @classmethod
    # def create_from_fx_value(cls, fx_value: int):
    #     return deepcopy(ARP_TYPES_BY_VALUE[fx_value])

    @classmethod
    def get_by_fx_value(cls, fx_value: int) -> "ArpType":
        return ARP_TYPES_BY_VALUE[fx_value]


SUPPORTED_ARP_TYPES = [
    # ArpType("", value=0)  # 0 is empty arp. It disables previously running arp.
    # not sure if it act like OFF fore single notes, though
    # todo: handle 0 value somehow

    # todo: check that value parameter is actually correct - i just assumed they are sorted started from 1, ascending
    ArpType("/ 8", value=1),
    ArpType("/ 6", value=2),
    ArpType("/ 4", value=3),
    ArpType("/ 3", value=4),
    ArpType("/ 2", value=5),
    ArpType("/ 1", value=6),

    ArpType("/.2", value=7),
    ArpType("/.3", value=8),
    ArpType("/.4", value=9),
    ArpType("/.6", value=10),
    ArpType("/.8", value=11),

    ArpType("\\ 8", value=12),
    ArpType("\\ 6", value=13),
    ArpType("\\ 4", value=14),
    ArpType("\\ 3", value=15),
    ArpType("\\ 2", value=16),
    ArpType("\\ 1", value=17),

    ArpType("\\.2", value=18),
    ArpType("\\.3", value=19),
    ArpType("\\.4", value=20),
    ArpType("\\.6", value=21),
    ArpType("\\.8", value=22),

    ArpType("R 8", value=23),
    ArpType("R 6", value=24),
    ArpType("R 4", value=25),
    ArpType("R 3", value=26),
    ArpType("R 2", value=27),
    ArpType("R 1", value=28),

    ArpType("R.2", value=29),
    ArpType("R.3", value=30),
    ArpType("R.4", value=31),
    ArpType("R.6", value=32),
    ArpType("R.8", value=33),
]

# mapping tracker value: arp type object
ARP_TYPES_BY_VALUE = {item.value: item for item in SUPPORTED_ARP_TYPES}
