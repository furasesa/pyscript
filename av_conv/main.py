from econv.options import parse_option
from econv.context import Probe
parsed_arg = parse_option()
import pathlib
video_ext = ["*.mp4", "*.avi", "*.flv", "*.3gp", "*.ts", "*.mpg", "*.mov", "*.mkv"]  # video
audio_ext = ["*.mp3", "*.aac", "*.webm", "*.flac", "*.wav"]  # audio
looking_ext = video_ext + audio_ext

c = Probe()
c.set_directory('tests/')
c.get_files()
# c.select_files()
c.probe_info()

# get_file = [(a, a) for a in [pathlib.Path.glob(pattern='**/'+ext) for ext in looking_ext]]


# conversion test
# kw_args = {
#     't': 10,
#     'f': 'mp4',
#     'vcodec': 'libx264',
#     'acodec': 'aac',
#     # 'video_bitrate': 400,
#     # 'audio_bitrate': 98,
# }
# stream = ffmpeg.input(filename_test)
# stream = ffmpeg.output(stream, 'out.mp4', **kw_args)
# stream = ffmpeg.overwrite_output(stream)
# ffmpeg.run(stream)


# example 1
# input = ffmpeg.input('in.mp4')
# audio = input.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
# video = input.video.hflip()
# out = ffmpeg.output(audio, video, 'out.mp4')