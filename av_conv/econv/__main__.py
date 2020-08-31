from .context import FileSelector
from .context import Probe
from .options import parse_option
from .convert import FFMPEG
import logging
from functools import reduce
import pathlib
import ffmpeg

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

    selected_file = FileSelector(directory).get_selected_files()
    probe = Probe(selected_file)
    probe.get_av_context()
    probed_duration = probe.get_duration()
    for file, duration in probed_duration:
        logging.info('filename : %s\tduration: %s' % (file, duration))

    logging.debug('args : %s' % args)
    ss = next((v for k, v in args if k == 'ss'), 0)
    t = next((v for k, v in args if k == 't'), None)
    to = next((v for k, v in args if k == 'to'), None)

    logging.debug('ss : %s, t : %s, to : %s' % (ss, t, to))

    if ss != 0:
        if t is not None:
            conv_duration = to_second(t)
        elif to is not None:
            conv_duration = to_second(to) - to_second(ss)
        else:
            conv_duration = duration - to_second(ss)
    else:
        conv_duration = duration

    # logging.debug('convert duration = %s' % conv_duration)

    for file_input in selected_file:
        name = pathlib.Path(file_input).stem
        extension = pathlib.Path(file_input).suffix
        logging.debug('name, ext = %s, %s' % (name, extension))
        parts = int(conv_duration / 60)
        last_part = int(conv_duration % 60)
        logging.debug('trim parts : %s, last : %s' % (parts, last_part))
        start_pts = to_second(ss)
        concatarg = 'in_file.trim(start_pts=' + str(start_pts) + ', duration=60),'
        for i in range(1, parts+1):
            start_pts += 60
            # in_file = name+'_part_'+str(i)+extension
            concatarg += 'in_file.trim(start='+str(start_pts)+', duration=60),'
        logging.debug('concatarg : %s' % concatarg)
        in_file = ffmpeg.input(file_input)
        test = (
            ffmpeg.concat(
                in_file.trim(start=0, duration=60),
                in_file.trim(start=60, duration=60),
                # in_file.trim(start_pts=120, end_pts=180),
            ).output('test.mp4').compile()
        )
        print(test)

        # run = (
        #     ffmpeg.concat(
        #         in_file.trim(start=0, duration=60),
        #         in_file.trim(start=60, duration=60),
        #         # in_file.trim(start_pts=120, end_pts=180),
        #     ).output('test.mp4').run()
        #
        # )



        # conv = FFMPEG.trim(in_file)

    # p.get_context_args(args)
