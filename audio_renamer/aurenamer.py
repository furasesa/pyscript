from __future__ import print_function, unicode_literals

import os
import sys
import fnmatch
import re

try:
    from tinytag import TinyTag
except ImportError:
    print("updating pip")
    os.system("python get-pip.py")
    print("audio-metadata dependency")
    os.system("pip install tinytag")
    sys.exit(1)

try:
    from PyInquirer import prompt
except ImportError:
    os.system("pip install PyInquirer")
    sys.exit(1)

supported_format = ["mp3", "flac", "wav", "ogg", "opus", "wma", "m4a", "m4b"]

data = {'file': []}
for file_match in os.listdir():
    for ext in supported_format:
        if file_match.endswith(ext):
            tag = TinyTag.get(file_match)
            old_name = file_match
            new_name = str(tag.artist)+" - "+str(tag.title)+"."+ext
            if not fnmatch.fnmatch(new_name, "?." + ext):
                new_name = re.sub(r'[:/?%^$@#!|<>]|\W+[(]+\D+[)]|\W+[(]+\d+\D+[)]|\W+[\[]+\D+[\]]', '', new_name)

            if not old_name == new_name:
                print('old :\t%s\nnew :\t%s\n' % (old_name, new_name))
                args = "rename \"%s\" \"%s\"" % (old_name, new_name)
                data['file'].append({'name': args})

file_selection = [
    {
        'type': 'checkbox',
        'qmark': '😃',
        'message': 'Select listed file',
        'name': 'filename',
        'choices': data['file'],
        'validate': lambda ans: 'no file' if len(ans) == 0 else True
    },
]
while True:
    try:
        selected = prompt(file_selection)
        num_selected_file = len(selected['filename'])
        if num_selected_file == 0:
            print('Please Select at least 1 file')
            pass
        else:
            for selected_file in selected['filename']:
                print(selected_file)
                os.system(selected_file)
            break

    except IndexError:
        print("empty list")
        break
