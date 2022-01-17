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
  - pattern 1 - 0x31  (dec 49) - note C#4 at step 00, track 1
  - pattern 4 -  0x3C  (dec 60) - note C5, track 1
- Offset 0x35 (dec 53)
  - pattern 1 - 0xFF (dec 255) - seems to be indication of an empty note step
  - pattern 4 - 0x3C (dec 60) - note C5, track 1

**Conclusions:**

Judging from offsets and assuming that empty note values are coded as 0xFF, it seems that one note step in .mtp file is encoded with 6 bytes: (53-29)/4 = 6. First two bytes are used to store note value. 

We can assume that the other 4 bytes are somehow used to store FX1/2 values and instrument number.

 We know that the maximum length of the pattern on Polyend Tracker is 8 bars, or 128 steps and when we reduce the length of the pattern, the notes are still stored there as we can than expand the pattern length and get notes back, so we know that tracker stores all 8 bars in the pattern file for each track no matter what. We can also infer that from the fact that all of the file sizes are the same.

Judging from the repeating pattern with FF bytes in the file we can assume that starting from 
0x1d the next 0x300 (dec 768) bytes are all dedicated to track one no matter the length of the pattern. We can check it easily: 768 bytes /16 steps /6 bytes per step = 8 bars. 

After these 768 bytes reserved for track 1 we can see there is a byte that (probably) denotes the end of this track and then the pattern repeats itself.

So the structure of the files seems to go like this:

1. (offset 0 )    27 bytes - header of the file, unknown format (yet)
2. (offset 0x1c , dec 28) 1 byte set to  1F, seems like some kind of delimeter? It could probably mean the length of the pattern, since 1F is 31 and the length of the pattern is 32 steps (2 bars) and it cannot be 0-steps, so it can be 0-based, meaning that if this byte is set to 0, then the length of the pattern is 1 step. But why exactly this same value is used before every track in the pattern? Polyend tracker does not support track of different length in the same pattern (is it something that they wanted to do but did not?) 
3. (offset 0x1d , dec 29) 768 bytes - track one sequencer steps
   1. 6 bytes per step:
      1. first 1 byte is note value, starting from 0 where 0 is C0. FF encodes empty note value.
      2. next 5 bytes in unknown format (for now)
4. (offset 0x31D dec 797 ) 1 byte - set to 0x1F (dec 31) by default, no idea yet what it means and seems like a delimeter for next track
5. (offset 0x31E, dec 798) 768 bytes - track two sequencer steps
   1. same as previous track, frames of 6 bytes per step
6. (offset 0x61E, dec 1566) 1 byte - set to 0x1F (dec 31) by default, same as the one before that
7. (offset 0x61F, dec 1567) 768 bytes - track three sequencer steps
   1. seqencer steps, 6 bytes per step
8. (offset 0x91F, dec 2335) 1 byte - set to 0x1F
9. (offset 0x920, dec 2336) 768 bytes - track four steps data
10. (offset 0xC20, dec 3104) 1 byte - set to 0x1F
11. (offset 0xc21, dec 3105) 768 bytes - track five data
12. (offset 0xf21, dec 3873) 1 byte - set to 0x1f
13. (offset 0xf22, dec 3874) - 768 bytes - track six data
14. (offset 0x1222, dec 4642) - 1 byte set to 0x1f
15. (offset 0x1223, dec 4643) - 768 bytes - track seven data
16. (offset 0x1523, dec 5411) - 1 byte set to 0x1f
17. (offset 0x1524, dec 5412) - 768 bytes - track eight data
18. (offset 0x1824, dec 6180) - 4 bytes of unknown data that differs per file, seems like some kind of checksum

What we still do not know:

1. What exactly is stored in the header of the file (first 27 bytes)
2. What exactly is encoded in the byte that precedes every track payload (most likely it's the pattern length that is duplicated for all tracks for some reason)
3. How exactly instrument, fx1 and fx2 types and fx1 and fx2 values are encoded in 5 bytes, we can assume that 1st byte is insturment number, second is fx1 type, 3rd fx1 value, 4th fx2 type and 5th fx2 value, that would be pretty straightforward. 
4. What are the last 4 bytes of a document (we can check how checksums are typically caclulated and try to caclulate actual checksums with various popular algos and compare them to the actual values in files.)

## Comparing pattern files 1 and 5, 6, 7

Pattern 5 has OFF note step instead of the actual note.

offset 0x1d in pattern 5 file contains FC value.

**Conclusion:**

- "note OFF" is encoded as FC

Pattern 6 file has a CUT note step

offset 0x1d in pattern 6 file contains FD value.

**Conclusion:**

- "Note CUT" is encoded as FD
  
Pattern 7 file has a FAD (fade) note step

offset 0x1d in pattern 7 file contains FE value.

**Conclusion:**

- "Note FAD" is encoded as FE


## Comparing pattern files 1 and 10

Pattern 1: note c#4 on track 1, instrument 1
Pattern 10: note c4 on same track with instrument 2

weirdly enough, there are a lot of differences in header and steps here (aside from notes, that are as expected) 

Lets skip this one for now, it could be a result of me trying to paste some date when creating this pattern.

**TODO** 

Revisit pattern 10 from this session (project qqptrns)

## Comparing pattern files 1 and 13 (0x0D)

Pattern 1: note c#4 on track 1, instrument 1
Pattern 13: note c4 on track 2 with instrument 2

Pattern 13 has 0x30 (C4 note) on offset 0x31e (track 2 sequence payload start)
the next byte is set to 0x02 instead (0x00 in pattern 1). So it seems, that the next byte (or at least some of its bits) represent a zero-based instrument number.

**Conclusions:**

The manual says: "A maximum number of 48 sample-based Instruments is available." - so we need at least 6 bits to encode instrument number. 6 bits give us a range 0...63 which adds up to 48 sample-based instruments plus 16 midi channels that are also considered to be instruments (e.g. instrument 64 is midi channel 16). 

So we can assume that 6 last bits of this byte offset after note byte are used for instrument number and we have 2 bits first left to represent something (what is there to represent with 4 possible values? There should be something, otherwise Polyend could easily give us 240 instruments + 16 midi channels per file with this file format, right?)  

## Comparing pattern files 1 and 18 (0x12)

Pattern 1: note c#4 on track 1, instrument 1, pattern length is 32 steps
Pattern 18: note c4 on track 1 with instrument 3, pattern length is 5 steps

for some reason there are a lot of differences between these files, similar case to pattern 10

**TODO**

Revisit this file

## Comparing pattern files 1 and 19 (0x13)

Pattern 1: note c#4 on track 1, instrument 1, pattern length is 32 steps
Pattern 19: note c4 on track 1 with instrument 3, pattern length is 6 steps

Every byte that goes before actual steps data in pattern 19 is set to 0x05 (dec 5) instead of 0x1F (31) in pattern 1

**Conclusion**

Our hunch was right - this number represents the length of the pattern.

Worth noting that every channel has it and its always the same across all channels. Is it some kind of a unimplemented feature Or something reserved for the future? What happens if we manually change some of the values and try loading the pattern in tracker?

## Project qqfx 

### Comparing pattern 5 to pattern 01 from project qqptrns

Seems like byte 5 in step frame represents type of FX1 (and not fx2 for some reason, it would make sense if fx1 type was in bute 3 of the frame, right after the instrument) and byte 6 represents the value.

Volume (velocity) seems to be represented by 0x12 (dec 18), value 100 for velocity is reprented as 0x64  (dec 100 - it's 1-based because volume can be zero).

It also seems like 

### Comparing pattern 5 to pattern 08

This pattern clearly confirms the following structure of the sequence step frame:


- byte 1 – note, zero based
- byte 2 - instrument, zero based
- byte 3 - type of FX2 (we know that 0x12 is volume/velocity)
- byte 4 - value of FX2
- byte 5 - type of FX1 
- byte 6 - type of FX 1


This is enough for us to create a basic parser and exporter to MIDI.

To create a more advanced one we'll have to add support for:

1. Chord FX - this effect basically outputs several notes at once with one instrument
2. Arpeggio FX - this effect outputs several notes in a sequence with predefined step between them until another step in the track is encountered

It would be also a good idea to get the numbers for every type of FX.


1F (dec 31) is Panning FX with 0 representing -50 (and 0x32 probably representing 0, center)