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

video_ext = ["*.mp4", "*.avi", "*.flv", "*.3gp", "*.ts", "*.mpg", "*.mov", "*.mkv"]  # video
audio_ext = ["*.mp3", "*.aac", "*.webm", "*.flac", "*.wav"]  # audio
looking_ext = video_ext + audio_ext


class Probe(object):
    """
    usage :
    init Class
    c = Probe()

    set directory default is '.'
    c.set_directory('tests/')

    to print scanned files
    c.get_files()

    to select what files to convert
    c.select_files()
    requires at least 1 file

    """

    def __init__(self):
        self.directory = pathlib.Path('.')
        self.file_list = []
        self.selected_files = []
        self.config_filename = 'config.ini'
        self.config = ConfigParser()
        self.load_config = False
        self.file_probe = []
        self.vkey = []
        self.akey = []

        # logging.debug('stream input : %s' % self.input)
        # probe = ffmpeg.probe(self.input)
        # self.video_context = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        # self.audio_context = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        # logging.debug('video context :\n%s' % self.video_context)
        # logging.debug('audio context :\n%s' % self.audio_context)

    def set_directory(self, path_dir):
        self.directory = pathlib.Path(path_dir)
        # scanning for looking ext in dir
        self.file_list = [(str(path), path.name) for get in [self.directory.glob(ext) for ext in looking_ext]
                          for path in get]
        logging.debug('scanned files in %s\n%s' % (self.directory, self.file_list))
        if len(self.file_list) == 0:
            logging.error('no file in list')
            pass

    def get_files(self):
        return self.file_list

    def select_files(self):
        if len(self.file_list) >= 1:
            try:
                self.selected_files = checkboxlist_dialog(
                    title="File Selection",
                    text="Please Choose file",
                    values=self.file_list
                ).run()
                logging.debug("selected result %s " % self.selected_files)
            except AssertionError as e:
                logging.error(e, "maybe no files found")

    def probe_info(self):
        def get_context(dct, *keys):
            for key in keys:
                if key in key_available:
                    return dct[key]
                else:
                    try:
                        logging.debug('trying [tags]%s : %s' % (key, dct['tags'][key]))
                        return dct['tags'][key]
                    except KeyError:
                        continue

        def to_second(time_str):
            try:
                return reduce(lambda x, y: x * 60 + float(y), time_str.split(":"), 0)
            except AttributeError as ae:
                logging.error("AttributeError : %s" % ae)
                return
            except ValueError as ve:
                logging.error("ValueError : %s" % ve)
                return

        if len(self.selected_files) == 0 and len(self.file_list) >= 1:
            logging.warning('requires at least 1 file')
            self.select_files()
            self.probe_info()
        elif len(self.selected_files) >= 1:
            # probe = [probe_result for a in self.selected_files for probe_result in ffmpeg.probe(a)]
            # logging.debug(probe)
            for i in self.selected_files:
                probe = ffmpeg.probe(i)
                video_context = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                audio_context = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                audio_only = True if video_context is None else False
                logging.debug(i)
                if audio_only:
                    logging.debug('audio only')
                    key_available = list(audio_context.keys())
                    acodec = get_context(audio_context, 'codec_name')
                    srate = get_context(audio_context, 'sample_rate')
                    bps = get_context(audio_context, 'bits_per_sample')
                    bitrate = get_context(audio_context, 'bit_rate')
                    duration = get_context(audio_context, 'duration', 'DURATION', 'DURATION-eng')
                    dur_in_sec = to_second(duration)
                    logging.debug('''
                    audio codec\t\t: %s
                    sample rate\t\t: %s
                    bits per sample\t: %s
                    bit rate\t\t: %s
                    duration\t\t: %s or %s second
                    ''' % (acodec, srate, bps, bitrate, duration, dur_in_sec))
                    # logging.debug(audio_context)
                else:
                    key_available = list(video_context.keys())
                    vcodec = get_context(video_context, 'codec_name')
                    profile = get_context(video_context, 'profile')
                    width = get_context(video_context, 'width', 'coded_width')
                    height = get_context(video_context, 'height', 'coded_height')
                    pix_fmt = get_context(video_context, 'pix_fmt')
                    duration = get_context(video_context, 'duration', 'DURATION', 'DURATION-eng')
                    dur_in_sec = to_second(duration)
                    logging.debug('''
                    video codec\t\t: %s
                    profile\t\t: %s
                    width\t\t: %s
                    heght\t\t: %s
                    pixel fmt\t\t: %s
                    duration\t\t: %s or %s second
                    ''' % (vcodec, profile, width, height, pix_fmt, duration, dur_in_sec))

    def set_config_name(self, config_name):
        self.config_filename = config_name

# class Stream(object):
#     def __init__(self, directory):
#         self.directory = directory
#         self.get_filename = [(a, a) for a in config if a is not 'DEFAULT'] if load_config else \
#             [(a, a) for b in [glob.glob(ext) for ext in looking_ext] for a in b]
