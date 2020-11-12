from .threader import ActivePool
from .options import get_main_args
from .options import get_global_args
from .context import ContextManager
import logging.config

global_args = get_global_args()
logging_level = global_args.get('verbosity') * 10
DEBUG_FORMAT = "%(levelname)s\t%(module)s\t:: %(funcName)10s : %(message)s"

LOG_CONFIG = {'version': 1,
              'formatters': {
                  # 'info': {'format': INFO_FORMAT},
                  'debug': {'format': DEBUG_FORMAT},
                  # 'error': {'format': ERROR_FORMAT}
              },
              'handlers': {
                  'console': {
                      'class': 'logging.StreamHandler',
                      'formatter': 'debug',
                      'level': logging_level
                  }
              },
              'root': {'handlers': ['console'], 'level': logging_level}
              }
logging.config.dictConfig(LOG_CONFIG)

