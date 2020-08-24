from __future__ import print_function, unicode_literals
import argparse
import logging
import os
import sys
import threading
import time
import pathlib
import glob
import collections
from functools import reduce
import math
from configparser import ConfigParser

# import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )

try:
    logging.debug("import prompt_toolkit-3.0.5")
    from prompt_toolkit import prompt
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.shortcuts import radiolist_dialog
    from prompt_toolkit.shortcuts import checkboxlist_dialog
    # from prompt_toolkit import print_formatted_text, HTML
    # from prompt_toolkit.styles import Style
    logging.debug("import ffmpeg-python 0.2.0")
    import ffmpeg
    # logging.debug("import click-7.1.2")
    # import click
except ImportError as e:
    logging.error("error importing %s" % e)
    sys.exit(1)


# init
config_filename = 'tc.ini'
config = ConfigParser()
parser = argparse.ArgumentParser(description='Easy FFMPEG convertion')
config_list_audio = ['of', 'ca', 'ss', 't', 'to', 'ba']
config_list_video = ['of', 'ca', 'cv', 'ss', 't', 'to', 'bv', 'ba', 'crf']
video_ext = ["*.mp4", "*.avi", "*.flv", "*.3gp", "*.ts", "*.mpg", "*.mov", "*.mkv"]  # video
audio_ext = ["*.mp3", "*.aac", "*.webm", "*.flac", "*.wav"]  # audio
looking_ext = video_ext + audio_ext


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def make_active(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('in-progress: %s', self.active)

    def make_inactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('in-progress: %s', self.active)


def choice(msg):
    while True:
        ch = input(msg + '[y/n]')
        if ch in ['y', 'n', 'Y', 'N']:
            break

    if ch == 'y' or ch == 'Y':
        return True
    else:
        return False


def get_duration(video_stream):
    # tags = dct['tags']
    tags_key = ['duration', 'DURATION-eng', 'DURATION']
    try:
        v = video_stream['duration']
        return v
    except KeyError:
        try:
            for f in tags_key:
                if f in video_stream['tags']:
                    return video_stream['tags'][f]
        except KeyError:
            logging.error("key list : \n%s" % video_stream)


def validation(dct, key):
    if key is 'ss' or key is 't' or key is 'to':
        try:
            return dct[key]
        except KeyError as ke:
            logging.error("KeyError in validation : %s" % ke)
            return '0'
    elif key is 'of':
        try:
            if dct[key] == 'webm':
                logging.debug('video or audio convertion')
                return dct[key]
            for ext in audio_ext:
                _, _ext = ext.split('.')
                if _ext == dct[key]:
                    logging.debug('audio extension: %s' % _ext)
                    return dct[key]
            for ext in video_ext:
                _, _ext = ext.split('.')
                if _ext == dct[key]:
                    logging.debug('video extension: %s' % _ext)
                    return dct[key]
        except KeyError as ke:
            logging.error("KeyError in validation : %s" % ke)
            return '0'

    else:
        try:
            logging.debug('returning %s: %s' % (key, dct[key]))
            return dct[key]
        except KeyError:
            return None


def to_sec(time_str):
    try:
        return reduce(lambda sum, d: sum * 60 + float(d), time_str.split(":"), 0)
    except AttributeError as ae:
        logging.error("AttributeError : %s" % ae)
        return
    except ValueError as ve:
        logging.error("ValueError : %s" % ve)
        return


# Argument Parser first
parser.add_argument('-ss', '--ss',
                    action='store',
                    help='trim start'
                    )
parser.add_argument('-t', '--t',
                    action='store',
                    help='trim to x second'
                    )
parser.add_argument('-to', '--to',
                    action='store',
                    help='trim to specific time'
                    )
parser.add_argument('-cv', '--cv',
                    action='store',
                    help='video codec = h264, libx264, hevc, libvpx-vp9'
                    )
parser.add_argument('-ca', '--ca',
                    action='store',
                    help='audio codec = aac, mp3, flac, wav'
                    )
parser.add_argument('-bv', '--bv',
                    action='store',
                    help='video bitrate'
                    )
parser.add_argument('-ba', '--ba',
                    action='store',
                    help='audio bitrate'
                    )
parser.add_argument('-crf', '--crf',
                    action='store',
                    help='21-28 can be less or more'
                    )
parser.add_argument('-fps', '--fps',
                    action='store',
                    help='fps=fps=x fps'
                    )
# parser.add_argument('-a', '--audio',
#                     action='store_true',
#                     help='audio only switch'
#                     )
parser.add_argument('-of', '--of',
                    action='store',
                    help='output format. example mkv, mp4 for video.\n'
                         'mp3, flac, wav, aac for audio'
                    )
parser.add_argument('-w', '--write',
                    action='store_true',
                    help='write to config file. to load use -l or --load'
                    )
parser.add_argument('-l', '--load',
                    action='store_true',
                    help='load config file'
                    )
parser.add_argument('-fr', '--fragment',
                    action='store',
                    default=60,
                    type=int,
                    help='convertion fragment duration for resume capabilities. 60s is default'
                    )

# Switches of argparser
parsed_arg = parser.parse_args()
# switches
audio_only = vars(parsed_arg).get('audio')
write_config = vars(parsed_arg).get('write')
load_config = vars(parsed_arg).get('load')
fmt = vars(parsed_arg).get('of')
fragment = vars(parsed_arg).get('fragment')

# pass selecting file if using load switch

config.read(config_filename)
get_filename = [(a, a) for a in config if a is not 'DEFAULT'] if load_config else \
    [(a, a) for b in [glob.glob(ext) for ext in looking_ext] for a in b]
get_filename.sort()

# choose file to process
try:
    selected_file = checkboxlist_dialog(
        title="File Selection",
        text="Please Choose file",
        values=get_filename
    ).run()
    logging.debug("selected result %s " % selected_file)
except AssertionError as e:
    logging.error(e, "maybe no files found")

kv = {key: vars(parsed_arg).get(key) for key in config_list_video if vars(parsed_arg).get(key) is not None}
conv_list = [{section: dict(config[section])} for section in selected_file] if load_config else \
    [{section: dict(kv)} for section in selected_file]
logging.debug('key:value:\n%s' % kv)
logging.debug('convert list:\n%s' % conv_list)

# save config to file -w switch
if write_config:
    for inlist in conv_list:
        for section in inlist:
            logging.debug('writing to file\n%s: %s\n' % (section, inlist[section]))
            config[section] = inlist[section]
            try:
                with open(config_filename, 'w') as cf:
                    config.write(cf)
            except OSError as oserr:
                logging.error("OS Error : %s" % oserr)


for file_input_list in conv_list:
    for section in file_input_list:
        dct_set = file_input_list[section]
        probe = ffmpeg.probe(section)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        ss = to_sec(validation(dct_set, 'ss'))
        t = to_sec(validation(dct_set, 't'))
        to = to_sec(validation(dct_set, 'to'))
        vcodec_i = video_stream['codec_name']
        vcodec_o = validation(dct_set, 'cv')
        acodec_i = audio_stream['codec_name']
        acodec_o = validation(dct_set, 'ca')
        fmt = validation(dct_set, 'of')
        # print(vcodec_i)
        # logging.debug('video stream:\n%s' % video_stream)
        # logging.debug('audio stream:\n%s' % audio_stream)
        duration = to_sec(get_duration(video_stream))
        if t == 0 and to == 0:
            end_pts = duration
        else:
            if t != 0:
                end_pts = ss+t
            else:
                end_pts = to
        conv_duration = end_pts-ss if ss > 0 else end_pts
        part = int(conv_duration/60) if conv_duration > 60 else 1
        remain_sec = conv_duration%60
        logging.debug(
            """
            Stream Info:
            video codec : %s => %s
            audio codec : %s => %s
            
            Trim Info:
            trim start: %s  duration: %s or stop duration: %s
            Summary:
            video duration : %s sec  stop duration : %s sec
            convert duration : %s sec
            total fragment (%s) : %s sec remains: %s sec
            """ % (vcodec_i, vcodec_o,
                   acodec_i, acodec_o,
                   ss, t, to,
                   duration, end_pts,
                   conv_duration,
                   fragment, part, remain_sec)
        )


        """
        requires input duration
        """
        name = pathlib.Path(section).stem
        extension = pathlib.Path(section).suffix
        logging.debug('name : %s ext : %s' % (name, extension))
        exe_ = choice('convert '+name+extension+'now?')
        if exe_:
            for i in range(1, part, 1):
                # cache_log = open(section, "w+")
                mpart = i*fragment
                ss_now = ss+mpart
                file_output = name+'part'+str(i)
                file_output_ext = fmt if fmt is not None else extension
                stream = ffmpeg.input(section, ss=ss_now, t=fragment)
                stream = ffmpeg.output(stream, file_output+file_output_ext, )
                stream = ffmpeg.overwrite_output(stream)
                logging.debug('run (%s of %s)' % (i, part))
                ffmpeg.run(stream)

                # config['DEFAULT']['last'] = sec
                try:
                    logging.debug('writing log')
                    with open(config_filename, 'w') as cf:
                        config.write(cf)
                except OSError as oserr:
                    logging.error("OS Error : %s" % oserr)


        # print('section:', section)
        # print('f_args:', f_args)
        # print('ss', f_args['ss'])

        # stream = ffmpeg.input(section, ss=10, t=10)
        # stream = ffmpeg.hflip(stream)
        # stream = ffmpeg.output(stream, 'test.mp4')
        # stream = ffmpeg.overwrite_output(stream)
        # ffmpeg.run(stream)


        #
        # if audio_only:
        #     audio = stream.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
        #     out = (audio, 'out.mp3')
        # else:
        #     logging.debug('not yet')
        #     stream = ffmpeg.output(stream, 'test.mp4')
        #     stream = ffmpeg.overwrite_output(stream)

        # logging.debug('section: %s\nsetting: %s\n' % (section, inlist[section]))
        # for key in inlist[section]:
        #     locals()[key] = inlist[section][key]
        #     print(locals()[key])


# for section in selected_file:
#     probe = ffmpeg.probe(section)
#     in_aud_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
#     in_vid_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
#
#     in_vcodec = in_vid_stream['codec_name']
#     in_acodec = in_aud_stream['codec_name']

# get all setting here


sys.exit(1)

for i in filename:
    name, ext = os.path.splitext(i)

    """
    TODO :
    probe file info
    get setting
    write to tc.ini
    """
    # Probe File Info
    probe = ffmpeg.probe(i)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    duration = find_duration(video_stream)
    codec_name = video_stream['codec_name']
    # width = int(video_stream['width'])
    # height = int(video_stream['height'])

    # save to tc.ini
    config_writer(i)
    logging.debug("""
    filename\t\t: %s (%s)
    codec\t\t: %s => %s
    width\t\t: %s
    height\t\t: %s
    duration\t\t: %s
    """ % (name, ext, codec_name, vcodec, width, height, duration))

    # in1 = ffmpeg.input(i)
    # if ss and trimt:
    #     logging.debug('input %s ss %s t %s' % (i, ss, trimt))
    #     in1 = ffmpeg.input(i, ss=ss, t=trimt)
    # elif ss and to:
    #     # Requires ffmpeg version 4.x
    #     logging.debug('input %s ss %s to %s' % (i, ss, to))
    #     in1 = ffmpeg.input(i, ss=ss, to=to)
    # else:
    #     logging.debug('no trim')
    #     in1 = ffmpeg.input(i)

    # try:
    #     out.run()
    # except ffmpeg.Error as e:
    #     logging.error(e)

    # must be write config here
    config_writer(i)


# pool = ActivePool()
# semaphore = threading.Semaphore(thread_limit)


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
                file_input = "\"" + fc + "\""
                ofile = fc.replace(match_ext, oformat['ext'])
                output_file = "\"" + ofile + "\""
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
