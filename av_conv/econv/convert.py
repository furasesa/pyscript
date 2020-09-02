from .context import Probe
import ffmpeg
from .options import get_conversion_group
from .options import get_switch_args
from .options import get_filter_args
from .options import output_name
import pathlib
import logging


class Stream:
    def __init__(self):
        # parser = parse_option()
        # self.working_dir = vars(parser).get('directory')
        self.stream = None
        self.options = get_conversion_group()
        self.switches = get_switch_args()
        self.filters = get_filter_args()
        kwargs = self.options.get('kwargs')
        self._kwargs = self.options if kwargs is None else kwargs

        # result path and file name solver
        # self.result_path = None
        self.output_name = output_name()
        self.output_file = None
        self.output_extension = '.mp4'
        self.format = self.options.get('format')

    def input(self, input_file):
        parent = pathlib.Path(input_file).parent
        name = pathlib.Path(input_file).stem
        extension = pathlib.Path(input_file).suffix
        result_path = parent / 'result'
        self.output_extension = self.format if self.format is not None else extension

        if self.output_name is None:
            self.output_name = str(name)+str(self.output_extension)
        self.output_file = result_path / self.output_name

        self.stream = ffmpeg.input(str(input_file))
        if self.switches.get('hflip'):
            self.stream = ffmpeg.hflip(self.stream)
        if self.switches.get('vflip'):
            self.stream = ffmpeg.vflip(self.stream)
        self.stream = self.filter_handler()
        self.stream = ffmpeg.output(self.stream, str(self.output_file), **self._kwargs)

        # switch handler

        if self.switches.get('test'):
            logging.debug(self.compile())
        else:
            self.run(overwrite=True)

    def get_output(self):
        return self.output_file

    def filter_handler(self):
        if len(self.filters) > 0:
            # filter_args = {}
            logging.debug('has filter')
            key_list = list(self.filters.keys())
            if 'fps' in key_list:
                # fps_v = self.filters.get('fps')
                self.stream = ffmpeg.filter(self.stream, 'fps', fps=self.filters.get('fps'))

            if 'outer_crop' in key_list:
                v = self.filters.get('outer_crop')
                logging.debug('crop outer value : %s' % v)
                crop_arg = {}

                crop_key = dict(v).keys()
                left = 0
                bottom = 0
                right = 0
                top = 0
                if 'l' in crop_key:
                    left = int(dict(v).get('l'))
                elif 'left' in crop_key:
                    left = int(dict(v).get('left'))

                if 'b' in crop_key:
                    bottom = int(dict(v).get('b'))
                elif 'bottom' in crop_key:
                    bottom = int(dict(v).get('bottom'))

                if 'r' in crop_key:
                    right = int(dict(v).get('r'))
                elif 'right' in crop_key:
                    right = int(dict(v).get('right'))

                if 't' in crop_key:
                    top = int(dict(v).get('t'))
                elif 'top' in crop_key:
                    top = int(dict(v).get('top'))

                logging.debug('left: %s, bottom: %s, right: %s, top: %s' % (left, bottom, right, top))

                #begin
                w = 'iw-' + str(left + right)
                h = 'ih-' + str(top + bottom)
                x = str(left)
                y = 'ih-'+str(bottom)
                logging.debug('x:%s, y:%s, w:%s, h:%s' % (x, y, w, h))
                crop_arg.update({w: None, h: None, x: None, y: None})
                logging.debug('crop args : %s' % crop_arg)
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
