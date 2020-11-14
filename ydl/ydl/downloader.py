from __future__ import print_function, unicode_literals
import logging

import youtube_dl


class Downloader:
    def __init__(self):
        self.ydl_opt = {}
        self.postprocessors = []
        self.url = None

    def set_config(self, key, val):
        logging.debug('{}: {}'.format(key, val))
        self.ydl_opt.update({key: val})

    def set_postprocessors(self, pp_config):
        logging.debug('{}'.format(pp_config))
        self.postprocessors.append(pp_config)

    def set_url(self, link):
        self.url = link

    def run(self):
        if len(self.postprocessors) > 0:
            self.ydl_opt.update({
                'postprocessors': self.postprocessors
            })
        if self.url is not None:
            ydl_op = {
                'verbose': True,
                'format': '251',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '160'

                    },
                    {'key': 'FFmpegMetadata'},
                ],
            }
            logging.debug('download simulation:\nwith youtube_dl.YoutubeDL({}) as ydl:\n\tydl.download([{}])'
                          .format(self.ydl_opt, self.url))
            # youtube_dl.YoutubeDL(ydl_op).download([self.url])
            with youtube_dl.YoutubeDL(self.ydl_opt) as ydl:
                ydl.download([self.url])

    def test(self):
        if len(self.postprocessors) > 0:
            self.ydl_opt.update({
                'postprocessors': self.postprocessors
            })
        if self.url is not None:
            logging.debug('download simulation:\nwith youtube_dl.YoutubeDL({}) as ydl:\n\tydl.download([{}])'
                          .format(self.ydl_opt, self.url))


