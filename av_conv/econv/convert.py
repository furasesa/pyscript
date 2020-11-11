from .context import Probe
import ffmpeg
from .options import get_global_args
from .options import get_main_args
from .options import get_video_filter_args
from .options import get_audio_filter_args
from .options import get_special_args
from .options import get_fuctional_args
from .options import get_raw_output

from datetime import datetime
import pathlib
import logging
import sys


class Stream:
    def __init__(self):
        # static
        logging.debug('class stream __init__')
        self.stream = None
        self.stream_input = None
        self.stream_audio = None
        self.stream_video = None
        self.global_options = get_global_args()
        self.main_options = get_main_args()
        self.video_filters = get_video_filter_args()
        self.audio_filters = get_audio_filter_args()

        self.special_options = get_special_args()
        self.functional_options = get_fuctional_args()

        self.kwargs = self.main_options.get('kwargs')
        self.kwargs_generator()
        # self.stream.input by call
        # output init
        self.raw_output_name = get_raw_output()
        self.auto_increment = -1
        # self.output_name = ''
        self.output_file = ''

        # Setting
        self.total_file = 0
        self.using_filter_complex = False

        # probe
        self.probed_streams = []
        self.audio_only = False

        # working file
        self.working_file = ""
        # self.probed_input = None

    def kwargs_generator(self):
        # kwargs = self.options.get('kwargs')
        if self.kwargs is None:
            self.kwargs = self.main_options
        else:
            if len(self.main_options) > 1:
                # remove kwargs in option
                del self.main_options['kwargs']
                logging.debug('looking for options : %s' % self.main_options)
                # update self.kwargs for every options
                logging.debug('updating kwargs')
                self.kwargs.update(self.main_options)

        logging.debug('kwargs: %s' % self.kwargs)
        return self.kwargs

    def set_probed_streams(self, probed_streams):
        self.total_file = len(probed_streams)
        logging.debug("streams total: %s" % self.total_file)

        # set probed stream list
        self.probed_streams = probed_streams

    def setup_stream(self):
        for probed_file, probe in self.probed_streams:
            self.working_file = probed_file
            logging.debug('working file: %s' % self.working_file)
            self.stream_input = ffmpeg.input(str(self.working_file))
            logging.debug("stream input type: %s" % self.stream_input)
            # get to know
            video_context = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            audio_context = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            logging.debug("""
            video context: %s
            audio context: %s
            """ % (video_context, audio_context))
            if video_context is not None:
                self.stream_video = self.stream_input.video
                logging.debug("stream video type: %s" % self.stream_video)
            if audio_context is not None:
                self.stream_audio = self.stream_input.audio
                logging.debug("stream audio type: %s" % self.stream_audio)

    def global_args_handler(self):
        # global Nodes such as -y -loglevel
        verbosity = self.global_options.get('verbosity')
        logging.debug('verbosity level %s' % verbosity)
        '''
        python loglevel 1 DEBUG2, 2 INFO, 3 WARNING, 4 ERROR, 5 CRITICAL
        '''
        if verbosity == 1:
            self.kwargs.update({'loglevel': 'debug'})
        elif verbosity == 2:
            self.kwargs.update({'loglevel': 'info'})
        elif verbosity == 3:
            self.kwargs.update({'loglevel': 'warning'})
        elif verbosity == 4:
            self.kwargs.update({'loglevel': 'error'})
        elif verbosity == 5:
            self.kwargs.update({'loglevel': 'fatal'})

        if not self.global_options.get('banner'):
            self.kwargs.update({'hide_banner': None})

    def special_option_handler(self):
        if len(self.special_options) > 0:
            # if 'transpose' in self.special_options:
            #     v = self.special_options.get('transpose')
            #     self.kwargs.update({'vf': 'transpose='+str(v)})
            if 'meta_rotation' in self.special_options:
                v = self.special_options.get('meta_rotation')
                self.kwargs.update({'metadata:s:v': 'rotate=' + str(v)})

            if self.special_options.get('vn'):
                self.kwargs.update({'vn': None})
            if self.special_options.get('an'):
                self.kwargs.update({'an': None})
            logging.debug('kwargs update : %s' % self.kwargs)

    def video_filter_handler(self):
        # filter supported by python-ffmpeg
        if self.video_filters.get('hflip'):
            self.stream_video = self.stream_video.hflip()
        if self.video_filters.get('vflip'):
            self.stream_video = self.stream_video.vflip()
        if self.video_filters.get('fps'):
            self.stream_video = self.stream_video.filter('fps', self.video_filters.get('fps'))
        if self.video_filters.get('transpose'):
            self.stream_video = self.stream_video.filter('transpose', self.video_filters.get('transpose'))
        if self.video_filters.get('crop'):
            self.stream_video = self.stream_video.filter('crop', *self.video_filters.get('crop'))
        if self.video_filters.get('vfilter'):
            self.stream_video = self.stream_video.filter(*self.video_filters.get('vfilter'))

    def audio_filter_handler(self):
        def update(filter_name):
            if filter_name == 'aecho':
                logging.debug('special filter handler: aecho')
                if self.stream_audio is not None:
                    self.stream_audio = self.stream_audio.filter(
                        filter_name, *self.audio_filters.get(filter_name)
                    )
            else:
                if self.stream_audio is not None:
                    self.stream_audio = self.stream_audio.filter(
                        filter_name, self.audio_filters.get(filter_name)
                    )

        if 'volume' in self.audio_filters:
            update('volume')
        if 'aecho' in self.audio_filters:
            update('aecho')

        # if self.stream_audio is None:
        #     if self.audio_filters.get('volume'):
        #         logging.debug("set volume: %s" % self.audio_filters.get('volume'))
        #         self.kwargs.update({'af': 'volume='+self.audio_filters.get('volume')})
        # else:
        #     if self.audio_filters.get('aecho'):
        #         self.stream_audio = self.stream_audio.filter('aecho', *self.audio_filters.get('aecho'))
        #     if self.audio_filters.get('volume'):
        #         self.stream_audio = self.stream_audio.filter('volume', self.audio_filters.get('volume'))

    def output_handler(self, input_file):
        def auto_increment(start, width):
            # logging.debug('auto_increment type : %s : %s' % (type(self.auto_increment), self.auto_increment))
            if isinstance(self.auto_increment, str):
                int(self.auto_increment)
            if int(self.auto_increment) < 0:
                self.auto_increment = int(start)
            else:
                self.auto_increment += 1
            printed_auto_num = str(self.auto_increment)
            # logging.debug('printed_auto_num : %s' % printed_auto_num)
            args = printed_auto_num.zfill(width)
            logging.debug('args type: %s : %s' % (type(args), args))
            return args

        # extract path, name, extension from input_file
        parent = pathlib.Path(input_file).parent
        name = pathlib.Path(input_file).stem
        ext = pathlib.Path(input_file).suffix

        # create result path
        result_path = parent / 'result'
        result_path.mkdir(exist_ok=True)
        if self.raw_output_name is None:
            logging.debug('raw output name is None')
            output_name = str(name) + str(ext)
        else:
            # re init self.output_name
            output_name = ''
            if 'name' not in self.raw_output_name:
                logging.debug('name is not defined, use input name: %s' % name)
                output_name = name
            for k, v in self.raw_output_name.items():
                if k == 'name':
                    logging.debug('name: %s' % v)
                    if v == 'auto' or v == '':
                        output_name += name
                    else:
                        output_name += v
                elif k == 'ext':
                    logging.debug('given ext: %s' % v)
                    output_name += '.' + v
                elif k == 'ai':
                    width_value = len(str(v))
                    start_value = int(v)
                    logging.debug('start: %s, width: %s' % (start_value, width_value))
                    output_name += auto_increment(start_value, width_value)
                elif k == 'date':
                    now = datetime.now()
                    dt_string = now.strftime(v)
                    logging.debug('date: %s' % dt_string)
                    output_name += dt_string
                elif k == 'cnt':
                    logging.debug('total selected file: %s' % self.total_file)
                    output_name += str(self.total_file)
                else:
                    logging.debug('add string: %s' % k)
                    output_name += str(k)
            if 'ext' not in self.raw_output_name:
                logging.debug("extension is not defined, set ext: %s" % ext)
                output_name += ext

            logging.debug('now output name : %s' % output_name)
        self.output_file = str(result_path / output_name)
        logging.debug("output_file: %s" % self.output_file)

    def compile(self):
        return self.stream.compile()

    def run(self):
        # invoke kwargs
        self.global_args_handler()
        self.special_option_handler()

        # return filter complex
        self.video_filter_handler()
        self.audio_filter_handler()

        # output handler
        self.output_handler(self.working_file)

        # check stream

        # output
        if self.stream_video is None:
            self.stream = ffmpeg.output(
                # self.stream_input,
                self.stream_audio,
                self.output_file,
                **self.kwargs
            )
        elif self.stream_audio is None:
            logging.debug("Audio stream is None")
            self.stream = ffmpeg.output(
                # self.stream_input,
                self.stream_video,
                self.output_file,
                **self.kwargs
            )
        elif self.stream_audio is None and self.stream_video is None:
            logging.debug("using stream input")
            self.stream = ffmpeg.output(
                self.stream_input,
                self.output_file,
                **self.kwargs
            )
        else:
            logging.debug("using audio & video stream")
            self.stream = ffmpeg.output(
                self.stream_video,
                self.stream_audio,
                self.output_file,
                **self.kwargs
            )

        # switch handler
        if self.functional_options.get('test'):
            print(self.compile())
        else:
            try:
                self.stream.run(
                    overwrite_output=self.global_options.get('overwrite'),
                )
            except ffmpeg.Error as e:
                logging.error("error found : %s" % e)
