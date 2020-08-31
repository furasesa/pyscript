from .context import Probe
import ffmpeg

class FFMPEG:
    def __init__(self, stream_input, stream_output):
        self.si = stream_input
        self.so = stream_output

    # def trim(self, args):
