# Polyend Tracker MIDI Export tool

An effort to create a midi conversion tool for Polyend tracker project files. 

## Disclaimer

I am in no way affiliated with Polyend. This is a hobby project.


## Reverse Engineering

- [Pattern *.mtp files](reverse-engineering/patterns-reverse-engineering.md)
 
## TODOs

- ~~Pattern file parsing~~
- Render names for All FX types 
- Support rendering of all possible ranges of values for FXs
- Pattern MIDI export
  - ~~basic export~~
  - support for velocity (volume FX)
  - support for chord FX
  - support for arp FX
  - support for microtiming (micromove, `m`) FX
  - support for microtuning `M` fx (do midi files support that?) 
  - ~~cli tool for converting files~~
  - support for panning ([it seems](http://midi.teragonaudio.com/tech/midispec/pan.htm) to be supported by midi )
- Song arrangement MIDI export
  - export
  - extract BPM
  - cli tool for converting files
- PyPi package

