import os
import sys
from sys import argv

from polytrackermidi.parsers import patterns, project
from polytrackermidi.exporters import midi


def print_usage(message="", exit_program=True, exit_code=1):

    if message:
        print(message)
    print(f"Converts polyend tracker *.mtp pattern files to midi files"
          f"Usage:"            
          f"\npython {argv[0]} <input_filename.mtp> [<output_filename.mid>]")
    if exit_program:
        sys.exit(exit_code)


def main():
    # handle commandline args
    if len(argv) < 2:
        print_usage("Please provide a name of polyend tracker pattern file to parse")

    input_filename = argv[1]

    # generate output filename from an input one by changing extension
    # if provided
    if os.path.isdir(input_filename):

        output_filename = input_filename
        if not output_filename.endswith(os.sep):
            output_filename += os.sep

        output_filename += "project.mid"

    else:
        output_filename = ".".join(input_filename.split(".")[:-1]) + ".mid"

    try:
        # try to get output filename from second command line argument
        output_filename = argv[2]

        if output_filename.endswith(".mtp"):
            print(f"Are you sure you want to write output {output_filename}? It's an *.mtp file. Output is *.mid")
            sys.exit(1)
    except IndexError:
        # not provided - use default one
        pass

    if not (os.path.isfile(input_filename) or os.path.isdir(input_filename)):
        print(f"File {input_filename} does not exist")
        sys.exit(1)

    if os.path.isfile(output_filename):
        print(f"File {output_filename} already exists - will overwrite")

    if input_filename.endswith(".mtp"):
        print("Trying to parse a pattern file...")
        p = patterns.PatternParser(filename=input_filename)
        parsed_pattern = p.parse()

        # print(parsed_pattern.render_as_table())

        midi_exporter = midi.PatternToMidiExporter(pattern=parsed_pattern)
        midi_exporter.write_midi_file(output_filename)

        print(f"Exported pattern midi to {os.path.abspath(output_filename)}")

    else:
        print("Trying to parse a project...")
        # try to parse as project
        p = project.ProjectParser(filename_or_folder=input_filename)
        parsed_project = p.parse()

        # print(parsed_pattern.render_as_table())

        midi_exporter = midi.SongToMidiExporter(song=parsed_project.song)
        midi_exporter.write_midi_file(output_filename)

        print(f"Exported project midi to {os.path.abspath(output_filename)}")

        # todo: export individual patterns, too

        print("Trying to export patterns...")

        for number, pattern in parsed_project.song.pattern_mapping.items():
            midi_exporter = midi.PatternToMidiExporter(pattern=pattern, tempo_bpm=int(parsed_project.song.bpm))

            number_string = str(number)
            if len(number_string) < 2:
                number_string = "0" + number_string

            # create directory for patterns
            # in the same folder we export project to
            out_folder = os.sep.join(output_filename.split(os.sep)[:-1]) + os.sep

            try:
                os.mkdir(out_folder + "patterns_midi/")
            except FileExistsError:
                pass

            pattern_output_filename = out_folder + "patterns_midi/" + f"pattern_{number_string}.mid"
            midi_exporter.write_midi_file(pattern_output_filename)
            print(f"Exported pattern midi to {os.path.abspath(pattern_output_filename)}")



if __name__ == '__main__':

    main()
