from .context import FileSelector
from .context import Probe
from .options import parse_option
from .convert import Stream
import logging
from functools import reduce
import pathlib
from prompt_toolkit.shortcuts import yes_no_dialog
import sys

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
    stream = Stream()
    concat_file = vars(options).get('gen_concat')
    use_probe = vars(options).get('probe')
    # check if exist, replace or write to next line
    if concat_file is not None:
        p = pathlib.Path(concat_file)
        if p.exists():
            replace = yes_no_dialog(
                title='Concat Generator',
                text=concat_file + ' is exists. yes to replace, no to write to the next line').run()
            logging.debug('result dialog : %s' % replace)
            if replace:
                p.unlink()

    directory = FileSelector(vars(options).get('directory'))
    working_dir = directory.get_full_path()
    selected_file = directory.get_selected_files()

    if use_probe:
        probe = Probe(selected_file)
        probe.get_av_context()
        probed_duration = probe.get_duration()
        for file, duration in probed_duration:
            logging.info('filename : %s\tduration: %s' % (file, duration))

    if concat_file is not None:
        logging.info('writing %s for concatenate' % concat_file)
        with open(concat_file, 'a') as concat_writer:
            for f in selected_file:
                logging.info('writing file %s' % f)
                concat_writer.write('file \''+str(f)+'\'\n')

    else:
        for file_input in selected_file:
            logging.debug('file input : %s' % file_input)
            # name = pathlib.Path(file_input).stem
            # extension = pathlib.Path(file_input).suffix
            # logging.debug('path, name, ext = %s, %s, %s' % (working_dir, name, extension))
            stream.input(file_input)
