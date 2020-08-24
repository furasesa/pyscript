from __future__ import print_function, unicode_literals
import argparse
import logging
import os
import sys
import threading
import time

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )

try:
    from PyInquirer import prompt
except ImportError as e:
    logging.error("Please Install PyInquirer %s" % e)
    sys.exit(1)

try:
    import configparser
except ImportError:
    print("Config Parser import error")
    sys.exit(1)

video_format = ["mp4", "avi", "flv", "3gp", "ts", "mpg", "mov", "mkv"]
data = {'input_file': []}
for file_match in os.listdir():
    for i in video_format:
        if file_match.endswith(i):
            data['input_file'].append({
                'name': file_match
            })
            

prompt_config = prompt({
    'type': 'confirm',
    'name': 'confparser',
    'message': 'using config parser ?',
    'default': False
})

prompt_setting = [
    {
        'type': 'list',
        'name': 'hwaccel',
        'message': 'select your fav hardware accelaration',
        'choices': ['no', 'dxva2', 'd3d11va', 'cuda', 'cuvid', 'qsv'],
        'default': 'dxva2',
        'filter': lambda val: val.lower(),
    },
    {
        'type': 'confirm',
        'name': 'fflag',
        'message': 'add -fflags +autobsf+genpts+nofillin-igndts-ignidx ?',
        'default': False
    },

    {
        'type': 'confirm',
        'name': 'trim',
        'message': 'trim video ?',
        'default': False
    },
    {
        'type': 'input',
        'name': 'ss',
        'message': 'from [hh:mm:ss] :',
        'when': lambda answer: answer['trim'],
        'validate': lambda answer: 'At least 1 seconds format hh:mm:ss' if len(answer) == 0 else True
    },
    {
        'type': 'input',
        'name': 'to',
        'message': 'to [hh:mm:ss] :',
        'when': lambda answer: answer['trim'],
        'validate': lambda answer: 'At least 1 seconds format hh:mm:ss' if len(answer) == 0 else True
    },
    {
        'type': 'list',
        'name': 'profile',
        'message': 'select convertion profile bellow:',
        'choices': [
            ' -c:v libx264 -crf 21 -c:a aac ',
            ' -c:v libx264 -vf fps=fps=29 -crf 23 -c:a aac ',
            ' -c:v libx264 -crf 23 -maxrate 768K -bufsize 1M -c:a aac ',
            ' -c:v libx264 -crf 28 -maxrate 512K -bufsize 768K -vf fps=fps=29 -c:a aac ',
            ' -c:v libx265 -crf 28 -c:a aac ',
            'custom'
        ],
        'default': ' -c:v libx264 -crf 21 -c:a aac ',
        'filter': lambda val: val.lower(),
    },
    {
        'type': 'input',
        'name': 'profile',
        'message': 'set your codec : ',
        'when': lambda answer: answer['profile'] == 'custom',
        'validate': lambda answer: 'example -c for codec c:v video and c:a for audio' if len(answer) == 0 else True
    },

]

prompt_file = [
    {  # because validation is not working
        'type': 'checkbox',
        'qmark': '😃',
        'message': 'Select listed file',
        'name': 'filename',
        'choices': data['input_file'],
        'validate': lambda ans: 'no file' if len(ans) == 0 else True
    },
]

prompt_output_format = [
    {
        'type': 'list',
        'name': 'ext',
        'message': 'Video Format Container. select mp4 or mkv for better compression',
        'choices': ['mp4', 'mkv', 'webm', 'custom'],
        'default': 'mp4',
        'filter': lambda val: val.lower(),
    },
    {
        'type': 'input',
        'name': 'ext',
        'message': 'video extension format without dot',
        'when': lambda ans: ans['ext'] == 'custom',
        'validate': lambda ans: 'please type any' if len(ans) == 0 else True
    },

]


my_parser = argparse.ArgumentParser(description='queue conversion')
# Add the arguments
my_parser.add_argument('-t', '--threads', action='store', type=int, choices=range(1, 5), default=1)
args = my_parser.parse_args()
thread_limit = vars(args).get('threads')


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('in-progress: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('in-progress: %s', self.active)


def setting_validation(setting, section):
    if setting in section:
        # print(config[setting])
        if setting == 'cv':
            return ' -c:v ' + section[setting] + ' '
        elif setting == 'ca':
            return ' -c:a ' + section[setting] + ' '
        elif setting == 'bv':
            return ' -b:v ' + section[setting] + ' '
        elif setting == 'ba':
            return ' -b:a ' + section[setting] + ' '
        elif setting == 'no':
            return ''
        return ' -' + setting + ' ' + section[setting] + ' '
    else:
        return ''


def fflags_options(ans):
    if ans['fflag']:
        return " -fflags " + '"' + "+autobsf+genpts+nofillin-igndts-ignidx" + '" '
    else:
        return ''


def worker(s, p, cmd):
    logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        p.makeActive(name)
        logging.debug(cmd)
        os.system(cmd)
        time.sleep(0.1)
        p.makeInactive(name)


using_config = prompt_config['confparser']

if using_config:
    pool = ActivePool()
    semaphore = threading.Semaphore(thread_limit)
    logging.info('using config, reading config.ini')
    config = configparser.ConfigParser()
    config.read('config.ini')
    logging.info(config.sections())
    os.system('mkdir result')
    # arguments = []
    for fc in config.sections():
        for match_ext in video_format:
            if fc.endswith(match_ext):
                if 'output_format' in config[fc]:
                    ofile = fc.replace(match_ext, config[fc]['output_format'])
                    output_file = "\"" + ofile + "\""
                else:
                    logging.debug('force mp4 as output container video format')
                    ofile = fc.replace(match_ext, 'mp4')
                    output_file = "\"" + ofile + "\""

                file_input = "\"" + fc + "\""
                fflag = setting_validation('fflag', config[fc])
                threads = setting_validation('threads', config[fc])
                hwaccel = setting_validation('hwaccel', config[fc])
                ss = setting_validation('ss', config[fc])
                to = setting_validation('to', config[fc])
                cv = setting_validation('cv', config[fc])
                crf = setting_validation('crf', config[fc])
                maxrate = setting_validation('maxrate', config[fc])
                bufsize = setting_validation('bufsize', config[fc])
                vf = setting_validation('vf', config[fc])
                ca = setting_validation('ca', config[fc])
                ffscript = "ffmpeg" \
                           + fflag \
                           + hwaccel \
                           + threads \
                           + "-i " + file_input \
                           + ss \
                           + to \
                           + cv \
                           + crf \
                           + maxrate \
                           + vf \
                           + ca \
                           + ' result/' + output_file
                t = threading.Thread(target=worker, name="file " + fc, args=(semaphore, pool, ffscript))
                t.start()

else:
    answers = prompt(prompt_setting)
    hwaccel = setting_validation('hwaccel', answers)
    fflag = fflags_options(answers)
    ss = setting_validation('ss', answers)
    to = setting_validation('to', answers)
    codec = answers['profile']
    oformat = prompt(prompt_output_format)

    file_chosen = prompt(prompt_file)
    num_selected_file = len(file_chosen['filename'])
    # print(str(sel_file))
    while num_selected_file == 0:
        file_chosen = prompt(prompt_file)
        num_selected_file = len(file_chosen['filename'])

    os.system('mkdir result')

    pool = ActivePool()
    semaphore = threading.Semaphore(thread_limit)
    for fc in file_chosen['filename']:
        for match_ext in video_format:
            if fc.endswith(match_ext):
                file_input = "\""+fc+"\""
                ofile = fc.replace(match_ext, oformat['ext'])
                output_file = "\""+ofile+"\""
                logging.info("converting to \"%s\"", output_file)
                ffscript = "ffmpeg" \
                           + fflag \
                           + hwaccel \
                           + " -i " + file_input \
                           + ss \
                           + to \
                           + codec \
                           + ' result/' + output_file
                t = threading.Thread(target=worker, name="file " + fc, args=(semaphore, pool, ffscript))
                t.start()
