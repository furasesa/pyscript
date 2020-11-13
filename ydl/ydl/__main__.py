from .threader import ActivePool
import threading
import logging
import time
from .options import get_main_args
from .options import get_global_args
from .options import get_postprocessing_args
from .downloader import Downloader
# import youtube_dl
from youtube_dl.utils import format_bytes
from prompt_toolkit.shortcuts import checkboxlist_dialog
from .context import ContextManager



# def downloader(u_semaphore, u_pool, u_opts, u_url):
#     download_trial = 9
#     with u_semaphore:
#         name = threading.currentThread().getName()
#         u_pool.makeActive(name)
#         while not download_trial == 0:
#             try:
#                 # logging.debug('download options: %s\nurl: %s' % (u_opts, u_url))
#                 youtube_dl.YoutubeDL(u_opts).download(u_url)
#                 break
#             except youtube_dl.utils.DownloadError as err:
#                 # logging.error("some error %s" % err)
#                 download_trial -= 1
#                 msg = "trial download is ended" if download_trial == 0 else err
#                 logging.error(msg)
#         time.sleep(1)
#         pool.makeInactive(name)


if __name__ == '__main__':
    ydl = Downloader()
    ctm = ContextManager()

    main_args = get_main_args()
    global_args = get_global_args()
    postprocessing_args = get_postprocessing_args()

    # ydl_opts = {}
    # postprocessors = []

    pool = ActivePool()
    semaphore = threading.Semaphore(2)

    # read options
    # main
    url = main_args.get('input')
    get_list_format = main_args.get('list_format')

    # global
    verbosity = global_args.get('verbosity')
    ext_downloader = global_args.get('downloader')
    audio_only = global_args.get('audio_only')

    #post-processing
    extension = postprocessing_args.get('extension')

    if ext_downloader:
        # ydl_opts.update({'external_downloader': ext_downloader})
        ydl.set_config('external_downloader', ext_downloader)

    if verbosity > 0:
        # ydl_opts.update({'verbose': True})
        ydl.set_config('verbose', True)

    ctm.generate_info(url)
    # print(ctm.get_all_formats())
    # ydl.add_url(url)

    af = ctm.get_all_formats()

    for i in af:
        url = i.get('url')
        title = i.get('title')
        formats = i.get('format_selector')
        print('url\t{}'.format(url))
        print('title\t{}'.format(title))
        print('fmt\t{}'.format(formats))
        print('\n\n')
        selected_list = checkboxlist_dialog(
            title=title,
            text="link {}".format(url),
            values=formats
        ).run()

    # if get_list_format:
    #     print(ctm.get_raw_context())
    # else:
    #     if audio_only:
    #         selected_list = checkboxlist_dialog(
    #             title="Audio Only",
    #             text="Select Audio Source",
    #             values=ctm.get_audio_only_context()
    #         ).run()
    #         if len(selected_list) > 0:
    #             for format_queue_download in selected_list:
    #                 print('queue :', format_queue_download)
    #                 if extension is not None:
    #                     audio_format = extension
    #                 else:
    #                     audio_format = 'mp3'
    #                 ydl.set_config('format', format_queue_download)
    #                 ydl.set_postprocessing(
    #                     {
    #                         'key': 'FFmpegExtractAudio',
    #                         'preferredcodec': audio_format,
    #                         'preferredquality': '160',
    #                     },
    #                 )
    #                 ydl.set_postprocessing(
    #                     {
    #                         'key': 'FFmpegMetadata'
    #                     },)
    #                 # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #                 #     ydl.download([uri])
    #                 ydl.run()
    #     else:
    #         selected_list = checkboxlist_dialog(
    #             title="Download Quality",
    #             text="Please Select to download",
    #             values=ctm.get_filtered_context()
    #         ).run()
    #         print('total download :', len(selected_list), 'format :', selected_list)
    #         if len(selected_list) > 0:
    #             for format_queue_download in selected_list:
    #                 ydl.set_config('format', format_queue_download)

