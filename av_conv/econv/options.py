import argparse


def parse_option():
    parser = argparse.ArgumentParser(description='Easy FFMPEG convertion')
    # Argument Parser first
    parser.add_argument('-ss', '--ss',
                        action='store',
                        help='trim start'
                        )
    parser.add_argument('-t', '--t',
                        action='store',
                        help='trim to x second'
                        )
    parser.add_argument('-to', '--to',
                        action='store',
                        help='trim to specific time'
                        )
    parser.add_argument('-cv', '--cv',
                        action='store',
                        help='video codec = h264, libx264, hevc, libvpx-vp9'
                        )
    parser.add_argument('-ca', '--ca',
                        action='store',
                        help='audio codec = aac, mp3, flac, wav'
                        )
    parser.add_argument('-bv', '--bv',
                        action='store',
                        help='video bitrate'
                        )
    parser.add_argument('-ba', '--ba',
                        action='store',
                        help='audio bitrate'
                        )
    parser.add_argument('-crf', '--crf',
                        action='store',
                        help='21-28 can be less or more'
                        )
    parser.add_argument('-fps', '--fps',
                        action='store',
                        help='fps=fps=x fps'
                        )

    parser.add_argument('-of', '--of',
                        action='store',
                        help='output format. example mkv, mp4 for video.\n'
                             'mp3, flac, wav, aac for audio'
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
                        choices=range(1, 5, 1),
                        help='''
                        1 - DEBUG
                        2 - INFO
                        3 - WARNING
                        4 - ERROR
                        5 - CRITICAL
                        default is 4
                        '''
                        )
    return parser.parse_args()
