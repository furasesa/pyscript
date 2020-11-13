from __future__ import print_function, unicode_literals
import logging

import youtube_dl


class Downloader:
    def __init__(self):
        self.url = []
        self.ydl_opt = {}
        self.postprocessing = []

    def set_config(self, key, val):
        logging.debug('{}: {}'.format(key, val))
        self.ydl_opt.update({key: val})

    def set_postprocessing(self, pp_config):
        logging.debug('{}'.format(pp_config))
        self.postprocessing.append(pp_config)

    def add_url(self, url):
        self.url.append(url)

    def run(self):
        if len(self.postprocessing) > 0:
            self.ydl_opt.update({
                'postprocessing': self.postprocessing
            })
            # self.set_config('postprocessing', {self.postprocessing})
        logging.debug('length ydl_opts: {}'.format(len(self.ydl_opt)))
        logging.debug('ydl_opts: {}'.format(self.ydl_opt))

