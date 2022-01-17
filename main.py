# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    from parsers import patterns

    # todo: remove this and implement tests
    p = patterns.PatternParser(
        # NOTE: this file was created with 1.3.1 or older version
        filename="./reverse-engineering/session 1/project files/datagreed - rebel path tribute 2/patterns/pattern_06.mtp")
    parsed_pattern = p.parse()

    print(parsed_pattern)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
