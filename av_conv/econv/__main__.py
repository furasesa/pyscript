from .context import FileSelector
from .context import Probe
from .options import parse_option
from .convert import Stream
import logging
from functools import reduce
import pathlib

options = parse_option()


def to_second(time_str):
    try:
        return reduce(lambda x, y: x * 60 + float(y), time_str.split(":"), 0)
    except AttributeError as ae:
        logging.error("AttributeError : %s" % ae)
        return
    except ValueError as ve:
        logging.error("ValueError : %s" % ve)
        return


if __name__ == '__main__':
    directory = FileSelector(vars(options).get('directory'))
    working_dir = directory.get_full_path()
    selected_file = directory.get_selected_files()
    probe = Probe(selected_file)
    probe.get_av_context()
    probed_duration = probe.get_duration()
    for file, duration in probed_duration:
        logging.info('filename : %s\tduration: %s' % (file, duration))

    for file_input in selected_file:
        name = pathlib.Path(file_input).stem
        extension = pathlib.Path(file_input).suffix
        logging.debug('path, name, ext = %s, %s, %s' % (working_dir, name, extension))

        stream = Stream()
        stream.input(file_input)
        logging.debug(stream.compile())
        stream.run(overwrite=True)

 # logging.debug('args : %s' % args)
    # ss = next((v for k, v in args if k == 'ss'), 0)
    # t = next((v for k, v in args if k == 't'), None)
    # to = next((v for k, v in args if k == 'to'), None)
    #
    # logging.debug('ss : %s, t : %s, to : %s' % (ss, t, to))
    #
    # if ss != 0:
    #     if t is not None:
    #         conv_duration = to_second(t)
    #     elif to is not None:
    #         conv_duration = to_second(to) - to_second(ss)
    #     else:
    #         conv_duration = duration - to_second(ss)
    # else:
    #     conv_duration = duration

    # logging.debug('convert duration = %s' % conv_duration)