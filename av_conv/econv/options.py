import argparse


def parse_option():
    parser = argparse.ArgumentParser(description='Easy FFMPEG convertion')
    # Argument Parser first
    parser.add_argument('-ss', '--ss',
                        action='store',
                        help='start time time hh:mm:tt'
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
                        cv is video codec or vcodec. simply like h264, libx264, libvpx-vp9, libaom-av1
                        e.g. ffmpeg -c:v h264
                        experimental libaom-av1. full help ffmpeg -h encoder=libaom-av1
                        e.g. 
                        constant quality : ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -strict experimental av1_test.mkv
                        contrained quality : ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 2000k -strict experimental output.mkv
                        ffmpeg -i input.mp4 -c:v libaom-av1 -minrate 500k -b:v 2000k -maxrate 2500k -strict experimental output.mp4
                        When muxing into MP4, you may want to add -movflags +faststart to the output parameters if the intended use for the resulting file is streaming
                        '''
                        )
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
    parser.add_argument('-w', '--write',
                        action='store_true',
                        help='write to config file. to load use -l or --load'
                        )
    parser.add_argument('-l', '--load',
                        action='store_true',
                        help='load config file'
                        )
    parser.add_argument('-fr', '--fragment',
                        action='store',
                        default=60,
                        type=int,
                        help='convertion fragment duration for resume capabilities. 60s is default'
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
    return parser.parse_args()
