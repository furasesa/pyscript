import argparse
# import yaml
import logging
import textwrap as _textwrap
import re


class LineWrapRawTextHelpFormatter(argparse.RawTextHelpFormatter):
    def __add_whitespace(self, idx, iw_space, text):
        if idx == 0:
            return text
        return (" " * iw_space) + text

    def _split_lines(self, text, width):
        text_rows = text.splitlines()
        for idx, line in enumerate(text_rows):
            search = re.search('\s*[0-9\-]{0,}\.?\s*', line)
            if line.strip() == "":
                text_rows[idx] = " "
            elif search:
                lw_space = search.end()
                lines = [self.__add_whitespace(i, lw_space, x) for i, x in enumerate(_textwrap.wrap(line, width))]
                text_rows[idx] = lines

        return [item for sublist in text_rows for item in sublist]


def parse_option():
    parser = argparse.ArgumentParser(
        formatter_class=LineWrapRawTextHelpFormatter, )
    # global options
    global_group = parser.add_argument_group('global options')
    # Add the arguments
    global_group.add_argument('-a',
                              dest='audio_only',
                              action='store_true',
                              help='audio format',
                              )

    global_group.add_argument('--all',
                              dest='all_format',
                              action='store_true',
                              help='show all format',
                              )

    global_group.add_argument('-o', '--output',
                              action='store',
                              help='output format'
                              )

    global_group.add_argument('-v',
                              action='store',
                              dest='verbosity',
                              type=int,
                              default=3,
                              choices=range(1, 6, 1),
                              help='verbosity'
                              )

    global_group.add_argument('-d',
                              dest='downloader',
                              action='store',
                              help='external downloader'
                              )

    global_group.add_argument('--test',
                              dest='test',
                              action='store_true',
                              help='compile for debugging'
                              )

    global_group.add_argument('--ph', '--phone',
                              dest='phone',
                              action='store_true',
                              help='-o ~/storage/downloads/youtube-dl/'
                              )

    main_group = parser.add_argument_group('main options')
    main_group.add_argument('-i',
                            dest='input',
                            action='append',
                            help='add link',
                            required=True
                            )



    main_group.add_argument('-f',
                            dest='format_id',
                            action='store',
                            help='''
audio only format_id 139 140 = m4a; 251 webm
video only
360p30  243 webm; 134 mp4
480p30  244 webm; 135 mp4
720p30  247 webm; 136 mp4
720p60  302 webm; 298 mp4
1080p60 303 webm; 299 mp4
complete video
360p30  13  mp4
720p30  22  mp4
'''
                            )
    main_group.add_argument('-F',
                            dest='list_format',
                            action='store_true',
                            help='get raw format from json'
                            )

    postprocessing_group = parser.add_argument_group('post-processing')
    postprocessing_group.add_argument('--ext',
                                      dest='extension',
                                      action='store',
                                      help='output extension. aac, flac, mp3, m4a, opus, vorbis, wav'
                                      )

    postprocessing_group.add_argument('-q',
                                      dest='quality',
                                      action='store',
                                      # default=2,
                                      help='''
preffered quality. could be 0,1 or 128 for 128k of
bitrates. 0 is best. if uses bitrate it must not
to be greater than 160k.
'''
                                      )

    return parser.parse_args()


main_args = {}
global_args = {}
postprocessing_args = {}
options = parse_option()


def conversion_validation(group_args, key):
    v = vars(options).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        group_args.update({key: v})
    return


def get_global_args():
    conversion_validation(global_args, 'audio_only')
    conversion_validation(global_args, 'all_format')
    conversion_validation(global_args, 'output')
    conversion_validation(global_args, 'verbosity')
    conversion_validation(global_args, 'downloader')
    conversion_validation(global_args, 'test')
    conversion_validation(global_args, 'phone')
    return global_args


def get_main_args():
    # main options
    conversion_validation(main_args, 'input')
    conversion_validation(main_args, 'format')
    return main_args


def get_postprocessing_args():
    conversion_validation(postprocessing_args, 'extension')
    conversion_validation(postprocessing_args, 'quality')
    return postprocessing_args
