# Session 2 reverse engineering notes

Object: Polyend Tracker project `*.mt` files

## BPM reverse engineering

From docs:
goes from 40 to 800BPM

From files I have it seems that bpm fraction part and integer part are stored in different offsets.

integer part:
- 0x1c2  - 2 bytes long (could be more, need to check at 800 bpm)

examples:
- 120 bpm - F0 42
- 130 bpm - 02 43
- 131 bpm - 03 43
- 172 bpm - 2C 43  (am I mistaken? is it actually 171 bpm? would make more sense probably)
- 90? bpm - B4 42  (not sure if it was actually 90 bpm, gotta check)

no idea how to convert bpm values yet. I may have incorrectly named files according to bpms.
Have to double check and resave them.

project files conainns file name at the end and track names - hex viewer see tham as ascii.

Seems like some of my test files are saved with incorrectly according to their contents.

It seems that the song pattern sequence starts at 0x10 and each bytes represents a pattern number.

E.g. 01 01 02 stands for 1,1,2 patterns

so the offset seems to be 0x10 with length of 256 bytes 

