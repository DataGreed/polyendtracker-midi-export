# Polyend Tracker MIDI Export tool

MIDI conversion tool for Polyend Tracker project files. 

## Disclaimer

I am in no way affiliated with Polyend. This is a hobby project.

## Installation 

```sh
pip install polyendtracker-midi-export
```

## Usage

Converting Polyend Tracker `*.mtp` pattern file to midi (pattern files are nested in project folders under `patterns`):

```sh
$ polymidiexport ./my-tracker-project/patterns/pattern_02.mtp 
```

Specifying custom output file name:

```sh
$ polymidiexport ./my-tracker-project/patterns/pattern_02.mtp ./my-midi-file.mid
```

Converting Polyend Tracker `*.mtp` pattern file to a text file (outputs a table view of the 
pattern similar to how you see it in Tracker UI):

```sh
:$ python polytracker2text.py ./my-tracker-project/patterns/pattern_02.mtp 
```

You can see an example of pattern text representation [here](./reverse-engineering/session%201/project%20files/datagreed%20-%20rebel%20path%20tribute%202/patterns/pattern_01.txt)

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
- ~~PyPi package~~
- conversion web service

