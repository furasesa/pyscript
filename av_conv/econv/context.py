import ffmpeg
import logging
import pathlib
from configparser import ConfigParser
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog
from functools import reduce
from .options import parse_option
import sys

parser = parse_option()
video_ext = ["*.mp4", "*.avi", "*.flv", "*.3gp", "*.ts", "*.mpg", "*.mov", "*.mkv"]  # video
audio_ext = ["*.mp3", "*.aac", "*.webm", "*.flac", "*.wav"]  # audio
supported_ext = video_ext + audio_ext

all_ext = vars(parser).get('all_ext')
looking_ext = ["*.*"] if all_ext else supported_ext
logging.debug('looking ext : %s' % looking_ext)


def to_second(time_str):
    try:
        return reduce(lambda x, y: x * 60 + float(y), time_str.split(":"), 0)
    except AttributeError as ae:
        logging.error("AttributeError : %s" % ae)
        return
    except ValueError as ve:
        logging.error("ValueError : %s" % ve)
        return


def get_context(dct, all_key, *keys):
    for key in keys:
        if key in all_key:
            logging.debug('key : %s in %s' % (key, all_key))
            return dct[key]
        else:
            try:
                logging.debug('trying [tags]%s : %s' % (key, dct['tags'][key]))
                return dct['tags'][key]
            except KeyError:
                continue


class Probe(object):
    def __init__(self, selected_files):
        self.probed_file = []
        self.files_duration = []
        self.selected_probe = []
        for probe_this in selected_files:
            probe = ffmpeg.probe(probe_this)
            self.probed_file.append((probe_this, probe))

    def get_av_context(self):
        logging.info('probed file %s' % len(self.probed_file))
        return self.probed_file

    def get_duration(self):
        if len(self.probed_file) == 0:
            logging.error('probed file is zero')
        else:
            for file, p in self.probed_file:
                video_context = next((s for s in p['streams'] if s['codec_type'] == 'video'), None)
                audio_context = next((s for s in p['streams'] if s['codec_type'] == 'audio'), None)
                logging.info('file : %s\nvc :%s\nac: %s' % (file, video_context, audio_context))
                audio_only = True if video_context is None else False
                if audio_only:
                    akey = list(audio_context.keys())
                    duration = get_context(audio_context, akey, 'duration', 'DURATION', 'DURATION-eng')
                else:
                    vkey = list(video_context.keys())
                    duration = get_context(video_context, vkey, 'duration', 'DURATION', 'DURATION-eng')
                self.files_duration.append((file, to_second(duration)))
            return self.files_duration


class FileSelector(object):
    def __init__(self, path):
        self.dir = pathlib.Path(path)
        self.anchor = self.dir.anchor
        self.parent = self.dir.parent
        self.stem = self.dir.stem
        self.selected_files = []
        self.select_files()
        self.working_path = self.parent / self.stem

    def get_full_path(self):
        logging.debug('%s' % self.working_path)
        return self.working_path

    def get_selected_files(self):
        return self.selected_files

    def select_files(self):
        try:
            file_list = [(str(path), path.name) for get in [self.dir.glob(ext) for ext in looking_ext]
                         for path in get]
            if len(file_list) == 0:
                logging.error('no supported file found in %s' % self.dir)
                sys.exit(10)
            else:
                logging.info('file list : %s' % file_list)
            self.selected_files = checkboxlist_dialog(
                title="File Selection",
                text="Please Choose file",
                values=file_list
            ).run()
            return self.selected_files
        except AssertionError:
            logging.error('assertion is zero')
            sys.exit(11)
        except TypeError as te:
            logging.error('no file selected, variable is NoneType : %s' % te)
            sys.exit(12)


   # def get_context_args(self, args):
    #     if len(self.probed_file) == 0:
    #         logging.error('probed file is zero')
    #     else:
    #         for file, p in self.probed_file:
    #             video_context = next((s for s in p['streams'] if s['codec_type'] == 'video'), None)
    #             audio_context = next((s for s in p['streams'] if s['codec_type'] == 'audio'), None)
    #             logging.info('file : %s\nvc :%s\nac: %s' % (file, video_context, audio_context))
    #             audio_only = True if video_context is None else False
    #             akey = list(audio_context.keys())
    #             logging.debug('args : %s' % args)

    # audio_only = True if video_context is None else False
    # akey = list(audio_context.keys())
    # if not audio_only:
    #     vkey = list(video_context.keys())
    #     vcodec = get_context(video_context, vkey, 'codec_name')
    #     profile = get_context(video_context, vkey, 'profile')
    #     width = get_context(video_context, vkey, 'width', 'coded_width')
    #     height = get_context(video_context, vkey, 'height', 'coded_height')
    #     pix_fmt = get_context(video_context, vkey, 'pix_fmt')
    #     duration = get_context(video_context, vkey, 'duration', 'DURATION', 'DURATION-eng')
    #     dur_in_sec = to_second(duration)
    #     logging.info('file : %s' % probe_this)
    #     logging.info('''
    #     video stream
    #     vcodec      : %s
    #     profile     : %s
    #     width       : %s
    #     height      : %s
    #     pix fmt     : %s
    #     duration    : %s second
    #
    #     ''' % (vcodec, profile, width, height, pix_fmt, dur_in_sec))
    #
    # acodec = get_context(audio_context, akey, 'codec_name')
    # srate = get_context(audio_context, akey, 'sample_rate')
    # bps = get_context(audio_context, akey, 'bits_per_sample')
    # bitrate = get_context(audio_context, akey, 'bit_rate')
    # duration = get_context(audio_context, akey, 'duration', 'DURATION', 'DURATION-eng')
    # dur_in_sec = to_second(duration)
    # logging.info('''
    # audio stream
    # acodec      : %s
    # srate       : %s
    # bps         : %s
    # bitrate     : %s
    # duration    : %s second
    #
    # ''' % (acodec, srate, bps, bitrate, dur_in_sec))