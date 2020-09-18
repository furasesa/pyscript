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
When muxing into MP4, you may want to add -movflags +faststart to the output parameters 
if the intended use for the resulting file is streaming
bitstream filter -bsf switch
'''
    )
    # global options
    global_group = parser.add_argument_group('global options')
    global_group.add_argument('-v', '--verbosity',
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
    global_group.add_argument('-y', '--y',
                              dest='overwrite',
                              action='store_true',
                              help='overwrite existing file/s'
                              )
    global_group.add_argument('--banner',
                              dest='banner',
                              action='store_true',
                              help='show ffmpeg banner'
                              )

    # main options
    main_group = parser.add_argument_group('main options')
    main_group.add_argument('-ss',
                            action='store',
                            help='''Trim Start'''
                            )
    main_group.add_argument('-t',
                            action='store',
                            help='duration trim hh:mm:tt'
                            )
    main_group.add_argument('-to',
                            action='store',
                            help='trim to specific time hh:mm:tt'
                            )
    main_group.add_argument('-cv',
                            dest='vcodec',
                            action='store',
                            help='video codec. hevc, h264, libx264, libvpx-vp9,libaom-av1, etc\nsee: ffmpeg -codecs')
    main_group.add_argument('-ca',
                            dest='acodec',
                            action='store',
                            help='audio codec.aac, mp3, wav, flac, etc.\nsee: ffmpeg -codecs'
                            )
    main_group.add_argument('-bv',
                            dest='video_bitrate',
                            action='store',
                            help='video bitrate'
                            )
    main_group.add_argument('-ba',
                            dest='audio_bitrate',
                            action='store',
                            help='audio bitrate'
                            )
    main_group.add_argument('-crf',
                            action='store',
                            help=
                            '''The range of the CRF scale is 0–51, where 0 is lossless, 23 is the default, 
and 51 is worst quality possible.
e.g. ffmpeg -i input -c:v libx264 -crf 21
'''
                            )
    main_group.add_argument('-f',
                            dest='format',
                            action='store',
                            help='output format. concat, segment, matroska, mp4, etc.\n see ffmpeg -formats'
                            )

    main_group.add_argument('-c',
                            dest='codec',
                            action='store',
                            help='codec. -c copy. see ffmpeg -codecs'
                            )

    main_group.add_argument('-kw', '--kwargs',
                            dest='kwargs',
                            action='store',
                            type=yaml.load,
                            help='''usage -kw --kwargs "{dict}".
for custom arguments. format : -kw "{-map: 0, vn: None, metadata:s:v: rotate=90}" 
e.g. -kw "{vcodec: libx264, t: 20, acodec: aac, f: mp4, crf: 20}"
'''
                            )
    video_filter_group = parser.add_argument_group('video filters')
    video_filter_group.add_argument('-fps',
                                    dest='fps',
                                    action='store',
                                    help='e.g -fps 29 -fps 60.'
                                    )
    video_filter_group.add_argument('-hflip',
                                    dest='hflip',
                                    action='store_true',
                                    help='e.g. -hflip for horizontal flip'
                                    )
    video_filter_group.add_argument('-vflip',
                                    dest='vflip',
                                    action='store_true',
                                    help='e.g. -vflip for vertical flip'
                                    )
    video_filter_group.add_argument('-cr', '--crop',
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
    video_filter_group.add_argument('-rot', '--rotate',
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
    e.g.: -rot 1
    -vf "{transpose, 1}"
    -kw "{vf: transpose=1}"
    transpose requires re-encoding. to avoid, please use -rotm
    '''
                                    )
    video_filter_group.add_argument('-vf',
                                    dest='vfilter',
                                    type=yaml.load,
                                    action='store',
                                    help='''-vf "{fps, 24}". -vf "{transpose, 1}"'''
                                    )

    audio_filter_group = parser.add_argument_group('audio filter group')
    audio_filter_group.add_argument('-aecho',
                                    dest='aecho',
                                    type=yaml.load,
                                    action='store',
                                    help='''aecho (in_gain, out_gain, delay, decay)
e.g. -aecho {'0.8, 0.9, 1000, 0.3'}'''
                                    )
    audio_filter_group.add_argument('-vol', '--volume',
                                    dest='volume',
                                    type=str,
                                    action='store',
                                    help='''value: 0.5 1.5 or 10dB -5dB
e.g. -vol 10dB --volume 10dB -vol 1.5; for negative value: -vol=-10db or -vol 0.5'''
                                    )

    audio_filter_group.add_argument('-af',
                                    dest='afilter',
                                    type=yaml.load,
                                    action='store',
                                    help='''see: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters'''
                                    )

    # special group
    special_group = parser.add_argument_group('special group')
    special_group.add_argument('-rotm', '--metadata-rotation',
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
    special_group.add_argument('-an',
                               dest='an',
                               action='store_true',
                               help='no audio. take out audio stream'
                               )
    special_group.add_argument('-vn',
                               dest='vn',
                               action='store_true',
                               help='similiar to an, but video. tak out a video from stream'
                               )

    # fuctional group
    fuctional_group = parser.add_argument_group('functional group')
    fuctional_group.add_argument('-d', '--dir',
                                 dest='directory',
                                 action='store',
                                 default='.',
                                 help='-d path/to/dir'
                                 )

    fuctional_group.add_argument('-a', '--all',
                                 dest='all_ext',
                                 action='store_true',
                                 help='requires if you need to show all files in folder'
                                 )
    fuctional_group.add_argument('-o',
                                 dest='out',
                                 type=yaml.load,
                                 action='store',
                                 help='''
supported format name, auto_increment (ai), extension (ext), date (date), count (cnt)
name is string standard format.

ai (auto increment). ai: 1 will start from 1, thus ai: 01 start from 01,
e.g. -o "{name: example, ai: '007', ext: mkv}"
output: example007.mkv, example008.mkv, ..., example099.mkv,... etc

ext (extension). if None, the ext name is same as input. 
if defined all files selected are same file extension.

date format :
year = y: 2 digit Y: 4 digit
month = m: number B: name (Jan, Feb, so on)
day = d, H = hour, M: minute, S: second
e.g "{date: '%y%m%d-%H%M'}" output: 200918-0938

count (cnt). Total files selected.
other than above are treat like string or conjunction
e.g. "{date: '%y%m%d, name: _sequence_, ai: 1, _of_, cnt'}"
output: 20200918_sequence_1_of_4.flv; ....., 20200918_sequence_4_of_4.mkv
'''
                                 )

    fuctional_group.add_argument('--test',
                                 dest='test',
                                 action='store_true',
                                 help='test compiled'
                                 )
    fuctional_group.add_argument('--probe',
                                 dest='probe',
                                 action='store_true',
                                 help='--probe to probe input. --test to skip conversion'
                                 )
    fuctional_group.add_argument('--gen-concat',
                                 dest='gen_concat',
                                 action='store',
                                 help='generate for concat files. -d tests/confile --gen-concat test.txt'
                                 )

    # return all options
    return parser.parse_args()


main_args = {}
video_filter_args = {}
audio_filter_args = {}
special_args = {}
functional_args = {}
global_args = {}
option = parse_option()


def conversion_validation(group_args, key):
    v = vars(option).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        group_args.update({key: v})
    return


def get_main_args():
    # main options
    conversion_validation(main_args, 'ss')
    conversion_validation(main_args, 't')
    conversion_validation(main_args, 'to')
    conversion_validation(main_args, 'vcodec')
    conversion_validation(main_args, 'acodec')
    conversion_validation(main_args, 'video_bitrate')
    conversion_validation(main_args, 'audio_bitrate')
    conversion_validation(main_args, 'crf')
    conversion_validation(main_args, 'format')
    conversion_validation(main_args, 'codec')
    conversion_validation(main_args, 'kwargs')
    return main_args


def get_global_args():
    # global options: loglevel, report, max_alloc, y, n, ignore_unknown, filter_threads, filter_complex_threads
    # stats, max_error_rate, bits_per_raw_sample, vol
    conversion_validation(global_args, 'verbosity')
    conversion_validation(global_args, 'overwrite')
    conversion_validation(global_args, 'banner')
    return global_args


def get_video_filter_args():
    """
    filter supported by python-ffmpeg :
    colorchannelmixer, concat, crop, drawbox, drawtext, filter, filter_, filter_multi_output,
    hflip, hue, overlay, setpts, trim, vflip, zoompan
    :return: video_filter_args
    """
    conversion_validation(video_filter_args, 'fps')
    conversion_validation(video_filter_args, 'crop')
    conversion_validation(video_filter_args, 'hflip')
    conversion_validation(video_filter_args, 'vflip')
    conversion_validation(video_filter_args, 'transpose')
    conversion_validation(video_filter_args, 'vfilter')
    # conversion_validation(filter_args, 'outer_crop')
    # conversion_validation(filter_args, 'qscalev')
    return video_filter_args


def get_audio_filter_args():
    """
    audio filter :

    :return: audio_filter_args
    """
    conversion_validation(audio_filter_args, 'aecho')
    conversion_validation(audio_filter_args, 'volume')
    conversion_validation(audio_filter_args, 'afilter')
    return audio_filter_args


def get_special_args():
    conversion_validation(special_args, 'meta_rotation')
    conversion_validation(special_args, 'an')
    conversion_validation(special_args, 'vn')
    return special_args


def get_fuctional_args():
    # used by __main__
    conversion_validation(functional_args, 'directory')
    conversion_validation(functional_args, 'all_ext')
    conversion_validation(functional_args, 'out')
    conversion_validation(functional_args, 'probe')
    conversion_validation(functional_args, 'gen_concat')
    conversion_validation(functional_args, 'test')
    return functional_args


def get_raw_output():
    v = functional_args.get('out')
    # v = vars(option).get('out')
    if v is not None:
        logging.debug('output filename : %s' % v)
        return v
    return None
