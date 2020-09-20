from .options import get_global_args
import logging
import logging.config

options = get_global_args()
logging_level = options.get('verbosity') * 10

# logging format
# ERROR_FORMAT = "%(levelname)s\t%(module)s\t:: %(funcName)10s %(lineno)S : %(message)s"
DEBUG_FORMAT = "%(levelname)s\t%(module)s\t:: %(funcName)10s : %(message)s"
# INFO_FORMAT = "%(module)s\t:: %(funcName)10s : %(message)s"
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

# logging.getLogger().setLevel(logging_level)
# logging.info("INFO")
# logging.debug("DEBUG")
# logging.getLogger().setLevel(10)
# logging.info("INFO")
# logging.debug("DEBUG")
