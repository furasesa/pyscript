@echo off

echo build econv
pip install -r requirements.txt
python setup.py install --user

echo make executive file
pyinstaller -F econv/main.py -n econv