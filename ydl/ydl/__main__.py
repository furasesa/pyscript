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
    webm_video_list = ctm.get_webm_video_list()
    mp4_video_list = ctm.get_mp4_video_list()
    va_list = ctm.get_va_list()

    # threading init
    pool = ActivePool()
    semaphore = threading.Semaphore(2)

    # options args init
    main_args = get_main_args()
    global_args = get_global_args()
    postprocessing_args = get_postprocessing_args()
    # main
    url = main_args.get('input')
    get_list_format = main_args.get('list_format')
    # global
    verbosity = global_args.get('verbosity')
    ext_downloader = global_args.get('downloader')
    is_audio_only = global_args.get('audio_only')
    is_all_format = global_args.get('all_format')
    test_dbg = global_args.get('test')

    # post-processing
    extension = postprocessing_args.get('extension')
    quality = postprocessing_args.get('quality')

    # variables
    format_choose = []
    queue_downloads = []

    # options to config
    if ext_downloader:
        ydl.set_config('external_downloader', ext_downloader)

    if verbosity > 0:
        ydl.set_config('verbose', True)

    # generate context from url
    ctm.generate_info(url)

    # show all formats
    if is_all_format:
        all_formats = ctm.get_all_formats()
        for fmts in all_formats:
            url = fmts.get('url')
            title = fmts.get('title')
            formats = fmts.get('format_selector')

            selected_list = checkboxlist_dialog(
                title=title,
                text="link {}".format(url),
                values=formats
            ).run()

            if '140' in selected_list:
                format_choose = ['140+'+v for v in mp4_video_list if v in selected_list]
            elif '251' in selected_list:
                format_choose = ['251+' + v for v in webm_video_list if v in selected_list]
            else:
                format_choose = None

            queue_downloads.append({'url': url, 'formats': format_choose})

    elif is_audio_only:
        audio_formats = ctm.get_audio_formats()
        if extension is not None:
            codec = extension
        else:
            codec = 'mp3'
        if quality is None:
            quality = '160'
        ydl.set_postprocessors(
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': quality,
            },
        )
        ydl.set_postprocessors(
            {
                'key': 'FFmpegMetadata'
            },)
        for fmts in audio_formats:
            url = fmts.get('url')
            title = fmts.get('title')
            formats = fmts.get('format_selector')
            selected_list = checkboxlist_dialog(
                title=title,
                text="link {}".format(url),
                values=formats
            ).run()
            format_choose = selected_list
            queue_downloads.append({'url': url, 'formats': format_choose})

    else:
        # default mode
        video_formats = ctm.get_video_formats()
        # print('\nvideo formats\n',video_formats)
        if extension is not None:
            ydl.set_postprocessors({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': extension,
            })
        for fmts in video_formats:
            url = fmts.get('url')
            title = fmts.get('title')
            formats = fmts.get('format_selector')
            selected_list = checkboxlist_dialog(
                title=title,
                text="link {}".format(url),
                values=formats
            ).run()
            format_choose = selected_list
            queue_downloads.append({'url': url, 'formats': format_choose})

    for downloads in queue_downloads:
        url = downloads.get('url')
        formats = downloads.get('formats')
        for f in formats:
            ydl.set_url(url)
            ydl.set_config('format', f)
            if test_dbg:
                ydl.test()
            else:
                ydl.run()




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

