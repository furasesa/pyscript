from .threader import ActivePool
from .options import get_main_args
from .context import ContextManager
import threading
import youtube_dl as ydl
import logging


def build_context(u_semaphore, u_pool, u_url):
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        try:
            info_dict = dict(ydl.YoutubeDL({'forcejson': True}).extract_info(u_url, download=False))
            print(info_dict)
            ctm = ContextManager(info_dict)
            print(ctm.get_codec_type())

        except ydl.utils.DownloadError as err:
            # logging.error(err)
            logging.error('some error found')


main_args = get_main_args()
url = main_args.get('input')

pool = ActivePool()
semaphore = threading.Semaphore(2)

for uri in url:
    threading.Thread(target=build_context, name="context builder",
                     args=(semaphore, pool, uri)).start()
