from .context import Probe
import ffmpeg
from .options import get_conversion_group
from .options import get_switch_args
from .options import get_filter_args
from .options import output_name
from .options import get_custom_filters
import pathlib
import logging


class Stream:
    def __init__(self):
        # static
        self.stream = None
        self.options = get_conversion_group()
        self.switches = get_switch_args()
        self.filters = get_filter_args()
        self.custom = get_custom_filters()

        self.output_name = output_name()
        self.output_file = None
        self.output_extension = '.mp4'
        self.format = self.options.get('format')

        kwargs = self.options.get('kwargs')

        if kwargs is None:
            self.kwargs = self.options
        else:
            self.kwargs = kwargs
            if len(self.options) > 1:
                logging.debug('options has more than kwargs, remove kwargs from options')
                # remove kwargs in option
                del self.options['kwargs']
                logging.debug('looking for options : %s' % self.options)
                # update self.kwargs for every options
                logging.debug('updating kwargs')
                self.kwargs.update(self.options)

        logging.debug('kwargs: %s' % self.kwargs)

    def input(self, input_file):
        # extract path, name, extension from input_file
        parent = pathlib.Path(input_file).parent
        name = pathlib.Path(input_file).stem
        extension = pathlib.Path(input_file).suffix
        # create result path
        result_path = parent / 'result'

        if self.output_name is None:
            self.output_name = str(name)+str(extension)
        self.output_file = result_path / self.output_name

        # set input stream
        self.stream = ffmpeg.input(str(input_file))

        # filter supported by python-ffmpeg
        if self.switches.get('hflip'):
            self.stream = ffmpeg.hflip(self.stream)
        if self.switches.get('vflip'):
            self.stream = ffmpeg.vflip(self.stream)
        self.stream = self.filter_handler()
        # custom filter
        self.custom_filter()

        # output
        self.stream = ffmpeg.output(self.stream, str(self.output_file), **self.kwargs)

        # switch handler

        if self.switches.get('test'):
            logging.debug(self.compile())
        else:
            self.run(overwrite=True)

    def get_output(self):
        return self.output_file

    def custom_filter(self):
        if len(self.custom) > 0:
            if 'transpose' in self.custom:
                v = self.custom.get('transpose')
                self.kwargs.update({'vf': 'transpose='+str(v)})
            if 'meta_rotation' in self.custom:
                v = self.custom.get('meta_rotation')
                self.kwargs.update({'metadata:s:v': 'rotate='+str(v)})

        logging.debug('kwargs update : %s' % self.kwargs)

    def filter_handler(self):
        def outer_crop_value(dct, *directions):
            keys = dict(dct).keys()
            for direction in directions:
                if direction in keys:
                    return dict(dct).get(direction)
            return -1

        if len(self.filters) > 0:
            # filter_args = {}
            logging.debug('has filter')
            key_list = list(self.filters.keys())
            if 'fps' in key_list:
                # fps_v = self.filters.get('fps')
                self.stream = ffmpeg.filter(self.stream, 'fps', fps=self.filters.get('fps'))

            if 'outer_crop' in key_list:
                dct = self.filters.get('outer_crop')
                logging.debug('crop outer value : %s' % dct)
                crop_arg = {}

                l = outer_crop_value(dct, 'l', 'left')
                t = outer_crop_value(dct, 't', 'top')
                b = outer_crop_value(dct, 'b', 'bottom')
                r = outer_crop_value(dct, 'r', 'right')

                no_crop_w = True if l < 0 and r < 0 else False
                no_crop_h = True if b < 0 and t < 0 else False

                logging.debug('left: %s, bottom: %s, right: %s, top: %s' % (l, b, r, t))

                #begin
                # logging.debug('use default width (w): %s; use default height (h): %s' % (no_crop_w, no_crop_h))
                x = '(in_w-out_w)/2' if no_crop_w else str(l)
                y = '(in_h-out_h)/2' if no_crop_h else str(t)

                w = 'iw' if no_crop_w else 'iw-' + str(l + r)
                h = 'ih' if no_crop_h else 'ih-' + str(t + b)
                logging.debug('x:%s, y:%s, w:%s, h:%s' % (x, y, w, h))

                crop_arg.update({w: None, h: None, x: None, y: None})
                # logging.debug('crop args : %s' % crop_arg)
                self.stream = ffmpeg.filter(self.stream, 'crop', *crop_arg)

            if 'crop' in key_list:
                logging.debug('crop args : %s' % self.filters.get('crop'))
                self.stream = ffmpeg.filter(self.stream, 'crop', *self.filters.get('crop'))
        return self.stream

    # def output(self):
    #     self.stream = ffmpeg.output(self.stream, str(self.output_file), **self._kwargs)

    def compile(self):
        return self.stream.compile()

    def run(self, overwrite):
        self.stream.run(overwrite_output=self.switches.get('overwrite'))
