from __future__ import print_function, unicode_literals

from .options import get_global_args
import logging.config
import youtube_dl

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

# tests
# ydl_opts = {
#         'format': '251/140',
#         'postprocessors': [
#             {
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '160'
#
#             },
#             {'key': 'FFmpegMetadata'},
#         ],
#     }
# print('__init__ youtube-dl test https://youtu.be/SWsStfj33Zg', ydl_opts)

# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])


