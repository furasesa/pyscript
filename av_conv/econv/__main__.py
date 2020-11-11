from .context import FileSelector
from .context import Probe
from .options import get_fuctional_args
from .convert import Stream
import logging
from functools import reduce
import pathlib
from prompt_toolkit.shortcuts import yes_no_dialog
import sys

options = get_fuctional_args()


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
    concat_file = options.get('gen_concat')
    print_probed_file = options.get('probe')
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

    directory = FileSelector(options.get('directory'))
    working_dir = directory.get_full_path()
    selected_file = directory.get_selected_files()

    # probe context
    probe = Probe(selected_file)
    stream.set_probed_streams(probe.get_probed_files())

    if print_probed_file:
        # probed_duration = probe.get_duration()
        print(probe.get_probed_files())

    # writing concat list to file
    if concat_file is not None:
        # generating concat file, skip conversion
        logging.info('writing %s for concatenate' % concat_file)
        with open(concat_file, 'a') as concat_writer:
            for f in selected_file:
                logging.info('writing file %s' % f)
                concat_writer.write('file \''+str(f)+'\'\n')

    else:
        # conversion
        for file in selected_file:
            stream.setup_stream()
            stream.run()
