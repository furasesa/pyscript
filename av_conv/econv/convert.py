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
        self.output_name = ''
        self.output_file = None
        self.total_file = 0

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

    def num_selected_file(self, v):
        self.total_file = v

    def input(self, input_file):
        # set input stream
        self.stream_input = ffmpeg.input(str(input_file))
        self.stream_audio = self.stream_input.audio
        self.stream_video = self.stream_input.video

        # invoke kwargs
        self.global_args_handler()
        self.special_option_handler()

        # return filter complex
        self.video_filter_handler()
        self.audio_filter_handler()

        # output handler
        self.output_handler(input_file)
        # output
        self.stream = ffmpeg.output(self.stream_audio, self.stream_video, str(self.output_file), **self.kwargs)
        # switch handler
        if self.functional_options.get('test'):
            print(self.compile())
        else:
            self.run()

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
                self.kwargs.update({'metadata:s:v': 'rotate='+str(v)})

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
        if self.audio_filters.get('aecho'):
            self.stream_audio = self.stream_audio.filter('aecho', *self.audio_filters.get('aecho'))
        if self.audio_filters.get('volume'):
            self.stream_audio = self.stream_audio.filter('volume', self.audio_filters.get('volume'))

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
            self.output_name = str(name)+str(ext)
        else:
            # re init self.output_name
            self.output_name = ''
            for k, v in self.raw_output_name.items():
                if k == 'name':
                    logging.debug('name: %s' % v)
                    self.output_name += v
                elif k == 'ext':
                    logging.debug('given ext: %s' % v)
                    self.output_name += '.'+v
                elif k == 'ai':
                    width_value = len(str(v))
                    start_value = int(v)
                    logging.debug('start: %s, width: %s' % (start_value, width_value))
                    self.output_name += auto_increment(start_value, width_value)
                elif k == 'date':
                    now = datetime.now()
                    dt_string = now.strftime(v)
                    logging.debug('date: %s' % dt_string)
                    self.output_name += dt_string
                elif k == 'cnt':
                    logging.debug('total selected file: %s' % self.total_file)
                    self.output_name += str(self.total_file)
                else:
                    logging.debug('add string: %s' % k)
                    self.output_name += str(k)

            if 'ext' not in self.raw_output_name:
                self.output_name += ext

            logging.debug('now output name : %s' % self.output_name)
        self.output_file = result_path / self.output_name

    def compile(self):
        return self.stream.compile()

    def run(self):
        self.stream.run(
            overwrite_output=self.global_options.get('overwrite'),
        )
