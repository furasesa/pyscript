from .threader import ActivePool
import threading
import logging
import time
from .options import get_main_args
from .options import get_global_args
import youtube_dl as ydl
from youtube_dl.utils import format_bytes


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


def format_note(fdict):
    res = ''
    if fdict.get('ext') in ['f4f', 'f4m']:
        res += '(unsupported) '
    if fdict.get('language'):
        if res:
            res += ' '
        res += '[%s] ' % fdict['language']
    if fdict.get('format_note') is not None:
        res += fdict['format_note'] + ' '
    if fdict.get('tbr') is not None:
        res += '%4dk ' % fdict['tbr']
    if fdict.get('container') is not None:
        if res:
            res += ', '
        res += '%s container' % fdict['container']
    if (fdict.get('vcodec') is not None
            and fdict.get('vcodec') != 'none'):
        if res:
            res += ', '
        res += fdict['vcodec']
        if fdict.get('vbr') is not None:
            res += '@'
    elif fdict.get('vbr') is not None and fdict.get('abr') is not None:
        res += 'video@'
    if fdict.get('vbr') is not None:
        res += '%4dk' % fdict['vbr']
    if fdict.get('fps') is not None:
        if res:
            res += ', '
        res += '%sfps' % fdict['fps']
    if fdict.get('acodec') is not None:
        if res:
            res += ', '
        if fdict['acodec'] == 'none':
            res += 'video only'
        else:
            res += '%-5s' % fdict['acodec']
    elif fdict.get('abr') is not None:
        if res:
            res += ', '
        res += 'audio'
    if fdict.get('abr') is not None:
        res += '@%3dk' % fdict['abr']
    if fdict.get('asr') is not None:
        res += ' (%5dHz)' % fdict['asr']
    if fdict.get('filesize') is not None:
        if res:
            res += ', '
        res += format_bytes(fdict['filesize'])
    elif fdict.get('filesize_approx') is not None:
        if res:
            res += ', '
        res += '~' + format_bytes(fdict['filesize_approx'])
    return res


def get_ydl_format(u_semaphore, u_pool, u_url):
    # formats = info_dict.get('formats', [info_dict])
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        # ydl_opts = {
        #     'forcejson': True,
        # }
        try:
            mdict = dict(ydl.YoutubeDL({'forcejson': True}).extract_info(u_url, download=False))
            formats = mdict.get('formats', [mdict])
            table = [
                [ydl.YoutubeDL.format_resolution(f), f['format_id'], f['ext'], format_note(f)]
                for f in formats
                if f.get('preference') is None or f['preference'] >= -1000]
            # logging.debug(formats)
            for t in table:
                print(t)
        except ydl.utils.DownloadError as err:
            # logging.error(err)
            logging.error('some error found')


if __name__ == '__main__':
    pool = ActivePool()
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

