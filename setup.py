from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name = 'polyendtracker-midi-export',
    version = '0.0.1',
    author = 'Alexey Strelkov',
    author_email = 'datagreed@gmail.com',
    license = 'MIT License',
    description = 'Unoficial tool that converts Polyend Tracker *.mtp pattern files to midi files.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/DataGreed/polyendtracker-midi-export',
    py_modules = ['parsers', 'exporters'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        polymidiexport=polytracker2midi:main
    '''
)