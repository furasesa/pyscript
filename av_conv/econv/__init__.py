from .options import get_global_args
import logging

options = get_global_args()
logging_level = options.get('verbosity')*10
logging.basicConfig(level=logging_level, format='(%(threadName)-10s) %(levelname)s\t%(module)s\t::'
                                                ' %(funcName)10s : %(message)s', )
