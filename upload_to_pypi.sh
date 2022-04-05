# must be run outside of virtual environment!
rm -rf dist/*
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel
python3 -m pip install --user --upgrade twine
python3 -m twine upload --repository pypi dist/* --verbose
