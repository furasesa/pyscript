import argparse
import yaml
import logging


def parse_option():
    parser = argparse.ArgumentParser(
        description='''
installing:
pip install -r requirements.txt
python setup.py install
usage:
python -m econv -d 'path to directory' [args or kwargs] [filters] [switches]
all switches are -- prefixes but -y (overwrite)
for help :
python -m econv -h
''',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
e.g. -kw "{codec: copy, bsf:v: h264_mp4toannexb, t: 10}"
experimental of libaom-av1
constant quality : 
originally : ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -t 10 -strict experimental out.mp4
e.g. -kw "{vcodec: libaom-av1, t: 10, crf: 30, video_bitrate: 0, strict: experimental}"
contrained quality : 
e.g. -kw "{vcodec: libaom-av1, t: 5, cpu-used: 5, crf: 30, video_bitrate: 2000, strict: experimental}"
e.g. -kw "{vcodec: libaom-av1, t: 5, minrate: 500, video_bitrate: 2000, maxrate: 2500, strict: experimental}"
When muxing into MP4, you may want to add -movflags +faststart to the output parameters if the intended use for the resulting file is streaming
bitstream filter -bsf switch
'''
    )
    # Argument Parser first
    parser.add_argument('-ss', '--ss',
                        action='store',
                        help='''Trim Start'''
                        )
    parser.add_argument('-t', '--t',
                        action='store',
                        help='duration trim hh:mm:tt'
                        )
    parser.add_argument('-to', '--to',
                        action='store',
                        help='trim to specific time hh:mm:tt'
                        )
    parser.add_argument('-cv', '--vcodec',
                        dest='vcodec',
                        action='store',
                        help='''
please see ffmpeg -codecs 
video codecs : hevc, h264, libx264, libvpx-vp9, libaom-av1
experimental libaom-av1. full help ffmpeg -h encoder=libaom-av1
''')
    parser.add_argument('-ca', '--acodec',
                        dest='acodec',
                        action='store',
                        help='''
ca is audio codec or acodec. simply like aac, mp3, wav, flac
e.g. ffmpeg -c:v libx264 -c:a aac
'''
                        )
    parser.add_argument('-bv', '--bv',
                        dest='video_bitrate',
                        action='store',
                        help='video bitrate'
                        )
    parser.add_argument('-ba', '--ba',
                        dest='audio_bitrate',
                        action='store',
                        help='audio bitrate'
                        )
    parser.add_argument('-crf', '--crf',
                        action='store',
                        help=''''
The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, 
and 51 is worst quality possible.
e.g. ffmpeg -i input -c:v libx264 -crf 21
'''
                        )

    parser.add_argument('-v', '--verbosity',
                        dest='verbosity',
                        type=int,
                        action='store',
                        default=4,
                        choices=range(1, 6, 1),
                        help='''
1 - DEBUG
2 - INFO
3 - WARNING
4 - ERROR
5 - CRITICAL
default is 4
'''
                        )
    parser.add_argument('-f', '--format',
                        dest='format',
                        action='store',
                        help='see ffmpeg -formats. e.g. -f mp4, -f matroska'
                        )

    parser.add_argument('-c', '--codec',
                        dest='codec',
                        action='store',
                        help='a codec. see ffmpeg -codecs. e.g. -c copy'
                        )
    
    parser.add_argument('-kw', '--kwargs',
                        dest='kwargs',
                        action='store',
                        type=yaml.load,
                        help='''
usage -kw --kwargs "{dict}". watch out white space after ':' vcodec:(space)libx264
video_bitrate: parameter for -b:v; audio_bitrate: parameter for -b:a
vcodec: parameter for -c:v; acodec: parameter for -c:a
f or fmt: parameter for format; fmt: mp4; f: mp4
e.g. -kw "{vcodec: libx264, t: 20, acodec: aac, f: mp4, crf: 20}"
'''
                        )

    parser.add_argument('-fps',
                        dest='fps',
                        action='store',
                        help='e.g -fps 29 -fps 60 etc'
                        )
    parser.add_argument('-cr', '--crop',
                        dest='crop',
                        type=yaml.load,
                        action='store',
                        help='''
full help : https://ffmpeg.org/ffmpeg-filters.html#crop
format -cr "{w, h, x, y}"
description:
w, out_w, ow is width of the cropped region default to iw
h, out_h, oh is height of the cropped region default to ih
in_w, iw is input width. aka input resolution (native resolution)
x is x pos; and y is y pos. 
e.g. x=0, y=0 is top left;
x, y blank means center of iw default to (in_w-out_w)/2 or (in_h-out_h)/2
the region w is xxx pixel to right, h is xxx pixel to top.
once x or y pos are specified, w=pixel region+x pixel, so h and y

e.g. to crop top of 100px and bottom 50px
-cr "{iw, ih-150, 0, ih-50}"
imagine that x= left -> x=0, y is 50px from bottom so y=50
create region so width is no change, means w=iw (original width size)
height region is top (ih) - (100px+ypos) so, h=ih-150
finnaly : {w=iw, h=ih-150, x=0, y=50 }

e.g. to crop left=10, right=10, top=20, bottom=20
-cr "{in_w-2*10, in_h-2*20}" or -cr "{in_w-20, in_h-40}"
x:y is zero mean at center position.
crop region :
w=iw-20 for each left and right side are -10
h=ih-40 for each top and bottom are -20
'''
                        )

    parser.add_argument('-cro', '--crop-outer',
                        dest='outer_crop',
                        type=yaml.load,
                        action='store',
                        help='''
e.g. to crop top of 100px and bottom 50px
-cr "{iw, ih-150, 0, ih-50}"    result crop=iw:ih-150:0:ih-50
-cro "{b: 50, t: 100}"          result crop=iw-0:ih-150:0:ih-50

e.g. to crop left=10, right=10, top=20, bottom=20
-cr "{in_w-20, in_h-40}"            result crop=iw-20:ih-40
-cro "{l: 10, r: 10, t: 20, b: 20}" result crop=iw-20:ih-40:10:ih-20 wrong
'''
                        )
    parser.add_argument('-rot', '--rotate',
                        dest='transpose',
                        type=int,
                        action='store',
                        choices=range(0, 4, 1),
                        help='''
video filter transpose. originally -vf transpose=number
0 - DEFAULT
1 - Rotate 90 Clockwise
2 - Rotate 90 Counter-Clockwise
3 - Rotate 90 Clockwise and flip
e.g. -rot 1
e.g. -kw "{vf: transpose=1}"
'''
                        )
    parser.add_argument('-rotm', '--metadata-rotation',
                        dest='meta_rotation',
                        type=int,
                        action='store',
                        help='''
rotation change by editing metadata.
-metadata:s:v rotate="90" -codec copy
this methode doesn't need re-encode, but player support.
e.g. -rotm or --metadata-rotation 90 -c:v copy -c:a copy
'''
                        )

    parser.add_argument('-d', '--dir',
                        dest='directory',
                        action='store',
                        default='.',
                        help='-d path/to/dir'
                        )

    parser.add_argument('-a', '--all',
                        dest='all_ext',
                        action='store_true',
                        help='requires if you need to show all files in folder'
                        )
    parser.add_argument('-o', '--out',
                        dest='out',
                        type=yaml.load,
                        action='store',
                        help='''
supported format name, auto_increment (ai), extension (ext)
e.g. -o "{name: example, ai: '007', ext: mkv}"
output: example007.mkv, example008.mkv, ..., example099.mkv,... etc
e.g. -o "{ai: '02', name: example, ext: mkv}"
output: 02example.mkv, 03example.mkv, ..., 10example... etc
'''
                        )
    parser.add_argument('-an',
                        dest='an',
                        action='store_true',
                        help='no audio. take out audio stream'
                        )
    parser.add_argument('-vn',
                        dest='vn',
                        action='store_true',
                        help='similiar to an, but video. tak out a video from stream'
                        )
    parser.add_argument('--test',
                        dest='test',
                        action='store_true',
                        help='test compiled'
                        )
    parser.add_argument('--hflip',
                        dest='hflip',
                        action='store_true',
                        help='e.g. --hflip for horizontal flip'
                        )
    parser.add_argument('--vflip',
                        dest='vflip',
                        action='store_true',
                        help='e.g. --vflip for vertical flip'
                        )
    parser.add_argument('-y', '--y',
                        dest='overwrite',
                        action='store_true',
                        help='force overwrite existing file/s'
                        )
    parser.add_argument('--banner',
                        dest='banner',
                        action='store_true',
                        help='--banner to show banner'
                        )
    parser.add_argument('--probe',
                        dest='probe',
                        action='store_true',
                        help='--probe to probe input. --test to skip conversion'
                        )
    parser.add_argument('--gen-concat',
                        dest='gen_concat',
                        action='store',
                        help='generate for concat files. -d tests/confile --gen-concat test.txt'
                        )
    return parser.parse_args()


conversion_args = {}
filter_args = {}
custom_args = {}
switch_args = {}
global_args = {}
option = parse_option()


def conversion_validation(group_args, key):
    v = vars(option).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        group_args.update({key: v})
    return


def get_conversion_group():
    # args with kwargs
    conversion_validation(conversion_args, 'ss')
    conversion_validation(conversion_args, 't')
    conversion_validation(conversion_args, 'to')
    conversion_validation(conversion_args, 'vcodec')
    conversion_validation(conversion_args, 'acodec')
    conversion_validation(conversion_args, 'video_bitrate')
    conversion_validation(conversion_args, 'audio_bitrate')
    conversion_validation(conversion_args, 'crf')
    conversion_validation(conversion_args, 'format')
    conversion_validation(conversion_args, 'codec')
    conversion_validation(conversion_args, 'kwargs')
    logging.debug('conversion_args : %s' % conversion_args)
    return conversion_args


def get_switch_args():
    conversion_validation(switch_args, 'test')
    conversion_validation(switch_args, 'hflip')
    conversion_validation(switch_args, 'vflip')
    return switch_args


def get_global_args():
    # global and args without kwrags
    conversion_validation(global_args, 'verbosity')
    conversion_validation(global_args, 'overwrite')
    conversion_validation(global_args, 'banner')
    conversion_validation(global_args, 'probe')
    conversion_validation(global_args, 'gen_concat')
    conversion_validation(global_args, 'an')
    conversion_validation(global_args, 'vn')
    return global_args


def get_filter_args():
    conversion_validation(filter_args, 'fps')
    conversion_validation(filter_args, 'crop')
    conversion_validation(filter_args, 'outer_crop')
    # conversion_validation(filter_args, 'qscalev')
    return filter_args


def get_custom_filters():
    conversion_validation(custom_args, 'transpose')
    conversion_validation(custom_args, 'meta_rotation')
    return custom_args


def get_raw_output():
    v = vars(option).get('out')
    if v is not None:
        logging.debug('output filename : %s' % v)
        return v
    return None
