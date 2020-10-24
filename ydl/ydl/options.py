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
    global_group.add_argument('-a', '--audio',
                              action='store_true',
                              help='get audio only source to download',
                              )

    global_group.add_argument('-o', '--output',
                              action='store',
                              help='output format'
                              )

    global_group.add_argument('-v', '--verbosity',
                              action='store',
                              help='output format'
                              )

    global_group.add_argument('-d', '--downloader',
                              action='store',
                              help='external downloader'
                              )

    main_group = parser.add_argument_group('main options')
    main_group.add_argument('-i', '--input',
                            action='append',
                            help='add link',
                            required=True
                            )

    main_group.add_argument('-q', '--quality',
                            action='store',
                            # default=2,
                            help='no'
                            )

    main_group.add_argument('-f', '--format',
                            action='store',
                            help='video source download'
                            )

    return parser.parse_args()


main_args = {}
global_args = {}
option = parse_option()


def conversion_validation(group_args, key):
    v = vars(option).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        group_args.update({key: v})
    return


def get_global_args():
    conversion_validation(global_args, 'audio')
    conversion_validation(global_args, 'output')
    conversion_validation(global_args, 'verbosity')
    conversion_validation(global_args, 'downloader')
    return global_args


def get_main_args():
    # main options
    conversion_validation(main_args, 'input')
    conversion_validation(main_args, 'quality')
    conversion_validation(main_args, 'format')
    return main_args

