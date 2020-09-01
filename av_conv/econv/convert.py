from .context import Probe
import ffmpeg
from .options import get_conversion_group
from .options import output_name
import pathlib
import logging


class Stream:
    def __init__(self):
        # parser = parse_option()
        # self.working_dir = vars(parser).get('directory')
        self.stream = None
        self.options = get_conversion_group()
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
        self.stream = ffmpeg.output(self.stream, str(self.output_file), **self._kwargs)

    def get_output(self):
        return self.output_file

    def filter(self, **kwargs):
        self.stream = ffmpeg.filter(self.stream, kwargs)

    # def output(self):
    #     self.stream = ffmpeg.output(self.stream, str(self.output_file), **self._kwargs)

    def compile(self):
        return self.stream.compile()

    def run(self, overwrite):
        self.stream.run(overwrite_output=overwrite)
