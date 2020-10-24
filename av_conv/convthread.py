import argparse
import logging
import os
import sys
import threading
import time

try:
    from PyInquirer import prompt
except ImportError:
    os.system("pip install PyInquirer")
    sys.exit(1)

try:
    import configparser

except ImportError:
    print("Config Parser import error")
    sys.exit(1)

my_parser = argparse.ArgumentParser(description='queue conversion')
# Add the arguments
my_parser.add_argument('-t', '--threads', action='store', type=int, choices=range(1, 5), default=1)
args = my_parser.parse_args()
thread_limit = vars(args).get('threads')
print(thread_limit)

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('Running: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('Running: %s', self.active)


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
        return ' -' + setting + ' ' + section[setting] + ' '
    else:
        return ''


def worker(s, pool, cmd):
    logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        logging.debug(cmd)
        os.system(cmd)
        time.sleep(0.1)
        pool.makeInactive(name)


pool = ActivePool()
s = threading.Semaphore(thread_limit)

video_format = ["mp4", "avi", "flv", "3gp", "ts", "mpg", "mov", "mkv"]
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
                output_filename = fc.replace(match_ext, config[fc]['output_format'])
            else:
                logging.info('force mp4 as output container video format')
                output_filename = fc.replace(match_ext, 'mp4')

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
                        + "-i " + fc \
                        + ss \
                        + to \
                        + cv \
                        + crf \
                        + maxrate \
                        + vf \
                        + ca \
                        + ' result/' + output_filename
            t = threading.Thread(target=worker, name="file "+fc, args=(s, pool, ffscript))
            t.start()

sys.exit(1)