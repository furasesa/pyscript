import argparse
import yaml
import logging




def parse_option():
    parser = argparse.ArgumentParser(
        description='''
installing:
python setup.py install
usage:
python -m econv -d 'path to directory'
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
    parser.add_argument('-fps', '--fps',
                        action='store',
                        help='''
                        e.g ffmpeg -i input -vf fps=fps=60
                        '''
                        )

    parser.add_argument('-f', '--format',
                        dest='format',
                        action='store',
                        help='''
                        e.g. file format ffmpeg -i input -f mp4
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
    parser.add_argument('-d', '--dir',
                        dest='directory',
                        action='store',
                        default='.',
                        help='''
                        -d 'path/to/dir'
                        '''
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
    parser.add_argument('-a', '--all',
                        dest='all_ext',
                        action='store_true',
                        help='''
requires if you need to show all files in folder
'''
                        )
    parser.add_argument('-o', '--out',
                        dest='out',
                        action='store',
                        help='''
output stream
if more than 1 file selected, please don't use this switch, except merging output
e.g. -o test.mp4
'''
                        )
    return parser.parse_args()


conversion_args = {}
option = parse_option()


def conversion_validation(key):
    v = vars(option).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        conversion_args.update({key: v})
    return


def get_conversion_group():
    conversion_validation('ss')
    conversion_validation('t')
    conversion_validation('to')
    conversion_validation('vcodec')
    conversion_validation('acodec')
    conversion_validation('video_bitrate')
    conversion_validation('audio_bitrate')
    conversion_validation('crf')
    conversion_validation('format')
    conversion_validation('kwargs')
    conversion_validation('out')
    logging.debug('conversion_args : %s' % conversion_args)
    return conversion_args


def output_name():
    v = vars(option).get('out')
    if v is not None:
        logging.debug('output filename : %s' % v)
        return v
    return None


