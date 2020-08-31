from .context import FileSelector
from .context import Probe
from .options import parse_option
from .convert import FFMPEG
import logging
from functools import reduce

args = []
options = parse_option()


def option_validation(key):
    v = vars(options).get(key)
    if v is not None:
        logging.debug('%s : %s ' % (key, v))
        args.append((key, v))
    return


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
    option_validation('vcodec')
    option_validation('acodec')
    option_validation('ss')
    option_validation('t')
    option_validation('to')
    option_validation('bv')
    option_validation('ba')
    option_validation('crf')
    option_validation('format')
    directory = vars(options).get('directory')

    f = FileSelector(directory)
    p = Probe(f.get_selected_files())
    p.get_av_context()
    probed_duration = p.get_duration()

    for file, duration in probed_duration:
        logging.info('filename : %s\tduration: %s' % (file, duration))

    logging.debug('args : %s' % args)
    ss = next((v for k, v in args if k == 'ss'), None)
    t = next((v for k, v in args if k == 't'), None)
    to = next((v for k, v in args if k == 'to'), None)

    logging.debug('ss : %s, t : %s, to : %s' % (ss, t, to))

    if ss is not None:
        if t is not None:
            conv_duration = to_second(t)
        elif to is not None:
            conv_duration = to_second(to) - to_second(ss)
        else:
            conv_duration = duration - to_second(ss)
    else:
        conv_duration = duration

    logging.debug('convert duration = %s' % conv_duration)


    # p.get_context_args(args)

    # t1 = FFMPEG.trim()
