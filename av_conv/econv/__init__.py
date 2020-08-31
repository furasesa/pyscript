from .options import parse_option
import logging

parsed_arg = parse_option()
logging_level = vars(parsed_arg).get('verbosity')*10
logging.basicConfig(level=logging_level, format='(%(threadName)-10s) %(levelname)s\t%(module)s\t:: %(funcName)10s : %(message)s', )
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')
