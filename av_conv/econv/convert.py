from .context import Probe
import ffmpeg


class FFMPEG:
    def __init__(self, stream_input, stream_output):
        self.si = stream_input
        self.so = stream_output

    def trim(self, file_input, concatarg):
        in_file = ffmpeg.input(file_input)
        (
            ffmpeg.concat(concatarg)
                .output('out.mp4')
                .run()
        )
