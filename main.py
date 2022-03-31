
if __name__ == '__main__':

    from parsers import patterns, project

    # # todo: remove this and implement tests
    # p = patterns.PatternParser(
    #     # NOTE: this file was created with firmware 1.3.1 or older version
    #     filename="./reverse-engineering/session 1/project files/datagreed - rebel path tribute 2/patterns/pattern_06.mtp")
    # parsed_pattern = p.parse()
    # # print(parsed_pattern.render_as_table())
    # from exporters import midi
    #
    # midi_exporter = midi.PatternToMidiExporter(pattern=parsed_pattern)
    # print(midi_exporter.generate_midi())
    # midi_exporter.write_midi_file("./test_midi_file.mid")


    project = project.ProjectParser(
        filename_or_folder="./reverse-engineering/session 1/project files/datagreed - rebel path tribute 2/"
    )

    parsed_project = project.parse()
    print("Finished parsing project.")
    print(f"BPM: {parsed_project.bpm}")


