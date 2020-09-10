from .context import Probe
import ffmpeg
from .options import get_global_args
from .options import get_main_args
from .options import get_video_filter_args

from .options import get_special_args
from .options import get_fuctional_args
from .options import get_raw_output


from datetime import date
import pathlib
import logging


class Stream:
    def __init__(self):
        # static
        logging.debug('class stream __init__')
        self.stream = None
        self.global_options = get_global_args()
        self.main_options = get_main_args()
        self.video_filters = get_video_filter_args()

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

    def input(self, input_file):
        # set input stream
        self.stream = ffmpeg.input(str(input_file))

        # invoke kwargs
        self.global_args_handler()
        self.special_option_handler()

        # return self.stream
        self.stream = self.video_filter_handler()

        # output handler
        self.output_handler(input_file)
        # output
        self.stream = ffmpeg.output(self.stream, str(self.output_file), **self.kwargs)
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
        # return self.stream

    def special_option_handler(self):
        if len(self.special_options) > 0:
            if 'transpose' in self.special_options:
                v = self.special_options.get('transpose')
                self.kwargs.update({'vf': 'transpose='+str(v)})
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
            self.stream = ffmpeg.hflip(self.stream)
        if self.video_filters.get('vflip'):
            self.stream = ffmpeg.vflip(self.stream)

        # custom filters

        # def outer_crop_value(dct, *directions):
        #     keys = dict(dct).keys()
        #     for direction in directions:
        #         if direction in keys:
        #             return dict(dct).get(direction)
        #     return -1

        if len(self.video_filters) > 0:
            # filter_args = {}
            logging.debug('has filter')
            key_list = list(self.video_filters.keys())
            if 'fps' in key_list:
                # fps_v = self.filters.get('fps')
                self.stream = ffmpeg.filter(self.stream, 'fps', fps=self.video_filters.get('fps'))

            # issues:
            # wrong cutting logic
            # if 'outer_crop' in key_list:
            #     dct = self.filters.get('outer_crop')
            #     logging.debug('crop outer value : %s' % dct)
            #     crop_arg = {}
            #
            #     l = outer_crop_value(dct, 'l', 'left')
            #     t = outer_crop_value(dct, 't', 'top')
            #     b = outer_crop_value(dct, 'b', 'bottom')
            #     r = outer_crop_value(dct, 'r', 'right')
            #
            #     no_crop_w = True if l < 0 and r < 0 else False
            #     no_crop_h = True if b < 0 and t < 0 else False
            #
            #     logging.debug('left: %s, bottom: %s, right: %s, top: %s' % (l, b, r, t))
            #
            #     #begin
            #     # logging.debug('use default width (w): %s; use default height (h): %s' % (no_crop_w, no_crop_h))
            #     x = '(in_w-out_w)/2' if no_crop_w else str(l)
            #     y = '(in_h-out_h)/2' if no_crop_h else str(t)
            #
            #     w = 'iw' if no_crop_w else 'iw-' + str(l + r)
            #     h = 'ih' if no_crop_h else 'ih-' + str(t + b)
            #     logging.debug('x:%s, y:%s, w:%s, h:%s' % (x, y, w, h))
            #
            #     crop_arg.update({w: None, h: None, x: None, y: None})
            #     # logging.debug('crop args : %s' % crop_arg)
            #     self.stream = ffmpeg.filter(self.stream, 'crop', *crop_arg)

            if 'crop' in key_list:
                logging.debug('crop args : %s' % self.video_filters.get('crop'))
                self.stream = ffmpeg.filter(self.stream, 'crop', *self.video_filters.get('crop'))
        return self.stream

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

                elif k is 'date':
                    logging.debug('date: %s' % v)
                    '''
                    TODO
                    '''
            logging.debug('now output name : %s' % self.output_name)
        self.output_file = result_path / self.output_name

    def compile(self):
        return self.stream.compile()

    def run(self):
        self.stream.run(
            overwrite_output=self.global_options.get('overwrite'),
        )
