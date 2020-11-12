from .threader import ActivePool
import threading
import logging
import time
from .options import get_main_args
from .options import get_global_args
import youtube_dl as ydl
from youtube_dl.utils import format_bytes
from prompt_toolkit.shortcuts import checkboxlist_dialog
from .context import ContextManager


def downloader(u_semaphore, u_pool, u_opts, u_url):
    # logging.debug('downloading %s' % u_url)
    download_trial = 1
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        while not download_trial == 0:
            try:
                # logging.debug('download options: %s\nurl: %s' % (u_opts, u_url))
                ydl.YoutubeDL(u_opts).download(u_url)
                break
            except ydl.utils.DownloadError as err:
                # logging.error("some error %s" % err)
                download_trial -= 1
                msg = "trial download is ended" if download_trial == 0 else err
                logging.error(msg)
        time.sleep(1)
        pool.makeInactive(name)


def build_context(u_semaphore, u_pool, u_url):
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        try:
            return dict(ydl.YoutubeDL({'forcejson': True}).extract_info(u_url, download=False))
        except ydl.utils.DownloadError as err:
            # logging.error(err)
            logging.error('some error found')


if __name__ == '__main__':
    main_args = get_main_args()
    url = main_args.get('input')
    pool = ActivePool()
    semaphore = threading.Semaphore(2)

    for uri in url:
        # info_dict = threading.Thread(target=build_context, name="context builder",
        #                              args=(semaphore, pool, uri)).start()

        info_dict = dict(ydl.YoutubeDL({'forcejson': True}).extract_info(uri, download=False))
        ctm = ContextManager(info_dict)
        print(ctm.get_raw_context())
        print(ctm.get_filtered_context())

        selected_list = checkboxlist_dialog(
                    title="Download Quality",
                    text="Please Select to download",
                    values=ctm.get_raw_context()
                ).run()
        print(selected_list)
    # semaphore = threading.Semaphore(2)
    #
    # global_args = get_global_args()
    # main_args = get_main_args()
    #
    # is_audio_only = global_args.get('audio')
    # output_cfg = global_args.get('output')
    # verbosity = global_args.get('verbosity')
    # ext_downloader = global_args.get('downloader')
    #
    # url = main_args.get('input')
    # qua = main_args.get('quality')
    # fmt = main_args.get('format')

    # for uri in url:
    #     ydl_opts = {
    #         # 'format': fmt,
    #         # 'noplaylist': np,
    #         # 'outtmpl': destination,
    #         # 'keepvideo': True,
    #         # 'external_downloader': ext_downloader,
    #
    #     }
    #     threading.Thread(target=get_ydl_format, name="ydl_format_test",
    #                      args=(semaphore, pool, uri)).start()

