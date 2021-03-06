import os
import sys
from sys import argv

from polytrackermidi.parsers import patterns


def print_usage(message="", exit_program=True, exit_code=1):

    if message:
        print(message)
    print(f"Converts polyend tracker *.mtp pattern files to text table files"
          f"Usage:"            
          f"\npython {argv[0]} <input_filename.mtp> [<output_filename.txt>]")
    if exit_program:
        sys.exit(exit_code)


def main():
    # handle commandline args
    if len(argv) < 2:
        print_usage("Please provide a name of polyend tracker pattern file to parse")

    input_filename = argv[1]

    # generate output filename from an input one by changing extension
    # if provided
    output_filename = ".".join(input_filename.split(".")[:-1])  + ".txt"

    try:
        # try to get output filename from second command line argument
        output_filename = argv[2]

        if output_filename.endswith(".mtp"):
            print(f"Are you sure you want to write output {output_filename}? It's an *.mtp file. Output is *.txt")
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

    result = parsed_pattern.render_as_table()

    with open(output_filename, 'w') as out:
        out.write(result)



    print(f"Exported text table to {os.path.abspath(output_filename)}")


if __name__ == '__main__':

    main()
