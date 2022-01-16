# Reverse Engineering Session 1

Focus on Pattern Files (.mtp)

## Project qqptrns

## Comparing pattern files 1 and 2

Pattern 1: note c#4 on track 1, instrument 1
Pattern 2: note c4 on same track with same instrument

### Differences in files:

- Offset 0x1d (dec 29):
  - pattern 1 - 0x31  (dec 49)
  - pattern 2 -  0x30  (dec 48)
  - seems to be a note. 

**Conclusions:**

- Middle C (C4) is 0x30 (dec 48).
- First note is at offset 0x1d (dec 29)

Interestingly,  C4 in MIDI is usually 60 and the lowest note is 11. Seems like polyend tracker lowest note (C0)  is 0 (which makes sense).

- Last 4 bytes, offset 0x1824 (dec 6180)
  - pattern 1 - 0xD66FE7C7
  - pattern 2 - 0x66102B3A
  - no idea what it is. Could be some checksum?

## Comparing pattern files 1 and 4

- Pattern 1: 
  - note c#4 on track 1, instrument 1, step 00
- Pattern 4: 
  - note c5 on same track with same instrument, step 00
  - note c5 on step 04 (same track, same instr)

### Differences in files:

- Offset 0x1d (dec 29):
  - pattern 1 - 0x31  (dec 49) - note C4 at step 00, track 1
  - pattern 4 -  0x3C  (dec 60) - note C5, track 1
- Offset 0x35 (dec 53)
  - pattern 1 - 0xFF (dec 255) - seems to be indication of an empty note step
  - pattern 4 - 0x3C (dec 60) - note C5, track 1

Judginf from
  
