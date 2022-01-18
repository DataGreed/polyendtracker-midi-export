
if __name__ == '__main__':

    from parsers import patterns

    # todo: remove this and implement tests
    p = patterns.PatternParser(
        # NOTE: this file was created with firmware 1.3.1 or older version
        filename="./reverse-engineering/session 1/project files/datagreed - rebel path tribute 2/patterns/pattern_06.mtp")
    parsed_pattern = p.parse()

    print(parsed_pattern.render_as_table())
