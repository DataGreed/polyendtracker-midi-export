import os
import sys
from sys import argv

from parsers import patterns
from exporters import midi


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
    output_filename = ".".join(input_filename.split(".")[:-1])  + ".mid"

    try:
        # try to get output filename from second command line argument
        output_filename = argv[2]

        if output_filename.endswith(".mtp"):
            print(f"Are you sure you want to write output {output_filename}? It's an *.mtp file. Output is *.mid")
            sys.exit(1)
    except IndexError:
        # not provided - use default one
        pass

    if not os.path.isfile(input_filename):
        print(f"{input_filename} does not exist")
        sys.exit(1)

    if os.path.isfile(output_filename):
        print(f"{output_filename} already exists - will overwrite")

    p = patterns.PatternParser(filename=input_filename)
    parsed_pattern = p.parse()

    # print(parsed_pattern.render_as_table())

    midi_exporter = midi.PatternToMidiExporter(pattern=parsed_pattern)
    midi_exporter.write_midi_file(output_filename)

    print(f"Exported midi to {os.path.abspath(output_filename)}")


if __name__ == '__main__':

    main()
