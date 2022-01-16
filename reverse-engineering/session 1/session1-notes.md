# Reverse Engineering Session 1

Focus on Pattern Files (.mtp)

## Project qqptrns

## Comparing patter files 1 and 2

Pattern 1: note c#4 on track 1, instrument 1
Pattern 2: note c4 on same track with same instrument

### Differences in files:

- Offset 0x1d (dec 29):
  - pattern 1 - 0x31  (dec 49)
  - pattern 2 -  0x30  (dec 48)
  - seems to be a note. 

Conclusion: middle C is dec 48.

Interestingly,  C4 in MIDI is usually 60 and the lowest note is 11. Seems like polyend tracker lowest note (C0)  is 0 (which makes sense).

- Last 4 bytes, offset 0x1824 (dec 6180)
  - pattern 1 - 0xD66FE7C7
  - pattern 2 - 0x66102B3A
  - no idea what it is. Could be some checksum?
