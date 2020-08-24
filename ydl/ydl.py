from __future__ import print_function, unicode_literals

import argparse
import logging
import sys
import os
import textwrap
import threading
import time
from configparser import ConfigParser

try:
    from PyInquirer import prompt
except ImportError:
    os.system('pip install PyInquirer')
    sys.exit(1)

try:
    import youtube_dl
except ImportError:
    os.system('pip install youtube-dl')
    sys.exit(1)

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )

"""
TODO : defining function
class Pool to switch state of semaphore downloading and updating

def downloader (semaphore, pool, ydl_opts, url)
def updater (semaphore, pool)
"""


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('in-progress: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('in-progress: %s', self.active)


def downloader(u_semaphore, u_pool, u_opts, u_url):
    # logging.debug('downloading %s' % u_url)
    download_trial = 1
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        while not download_trial == 0:
            try:
                # logging.debug('download options: %s\nurl: %s' % (u_opts, u_url))
                youtube_dl.YoutubeDL(u_opts).download(u_url)
                break
            except youtube_dl.utils.DownloadError as err:
                # logging.error("some error %s" % err)
                download_trial -= 1
                msg = "trial download is ended" if download_trial == 0 else err
                logging.error(msg)
        time.sleep(1)
        pool.makeInactive(name)


def updater(u_semaphore, u_pool):
    logging.debug('updating youtube-dl using pip')
    with u_semaphore:
        name = threading.currentThread().getName()
        u_pool.makeActive(name)
        try:
            os.system('pip install -U youtube-dl')
            logging.debug('youtube-dl updated')
        except OSError:
            logging.error('some error when updating')


# convert pixel selection to int quality
def pixel_to_quality(p2q):
    if p2q == '1080p60':
        return 1
    elif p2q == '720p60':
        return 2
    elif p2q == '1080p':
        return 3
    elif p2q == '720p':
        return 4
    elif p2q == '480p':
        return 5
    else:
        return 5


# convert to format code -f
# src_ext is source extension
# quality is format code
def quality(src_ext, int_quality):
    if src_ext == 'mp4':
        return {
            1: '299+140/298+140/137+140',
            2: '298+140/137+140',
            3: '137+140/136+140',
            4: '136+140/135+140',
            5: '135+140/134+140'
        }.get(int_quality, 2)
    elif src_ext == 'webm':
        return {
            1: '303+251/302+251/248+251',
            2: '302+251/248+251',
            3: '248+251/247+251',
            4: '247+251/244+251',
            5: '244+251/243+251'
        }.get(int_quality, 2)
    else:
        return {
            # requires to other than youtube
            1: 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            2: 'best'
        }.get(int_quality, 2)


# selecting download source for both audio and video
video_source = ['webm', 'mp4']

# deprecated since only 2 good source 251/140
# audio_source = ['m4a', 'webm']

# select codec after downloading. requires for post processing
audio_codec = ['aac', 'flac', 'mp3', 'vorbis', 'opus']
video_codec = ['mp4', 'mkv']

# init default values
default_audio_codec = ''
default_audio_quality = ''
default_video_codec = ''
default_video_quality = ''
# init destination
destination = ''
# init youtube-dl options
ydl_opts = {}

# setup config parser
config = ConfigParser()
# read from config.ini to get default values

# init argument parser
argument_parser = argparse.ArgumentParser(
    prog='ydl.py',
    formatter_class=argparse.RawTextHelpFormatter,
    description='Youtube Downloader',
    usage='python %(prog)s -i [link] [options]',
    epilog=textwrap.dedent(
        '''
        example :
        audio only download.
        python ydl.py -i https://youtu.be/SWsStfj33Zg -a
        
        more faster setting. requires codec output format.
        python ydl.py -i https://youtu.be/SWsStfj33Zg -a -c mp3
        
        custom location. Please see your config.ini
        python ydl.py -i https://youtu.be/SWsStfj33Zg -a -c mp3 -o phone
        
        for video, silly argument
        python ydl.py -i https://youtu.be/SWsStfj33Zg
        
        requires some information like source extension from link.
        youtube has 2 main codec source for video. vp9 .webm and avc .mp4
        python ydl.py -i https://youtu.be/SWsStfj33Zg -f mp4 -q 2
        
        there is no -c (codec) yet because conversion time
        End of help
        '''
    )
)

if config.read('config.ini'):
    logging.info('found config file')
else:
    # create config when no config.ini found
    config['DEFAULT'] = {
        'audio_codec': 'mp3',
        'video_codec': 'mp4',
        'audio_quality': 1,
        'video_quality': 2
    }
    config['DESTINATION'] = {
        'test': 'result',
        'phone': '~/storage/downloads/Videos/youtube-dl'
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    # give default values
    default_audio_codec = 'mp3'
    default_audio_quality = '1'
    default_video_codec = 'mp4'
    default_video_quality = '2'

# read DEFAULT section
if 'DEFAULT' in config:
    logging.debug('Config has default section')
    default_audio_codec = config.get('DEFAULT', 'audio_codec')
    default_audio_quality = config.get('DEFAULT', 'audio_quality')
    default_video_codec = config.get('DEFAULT', 'video_codec')
    default_video_quality = config.get('DEFAULT', 'video_quality')

# Add the arguments
argument_parser.add_argument('-a', '--audio',
                             action='store_true',
                             help='get audio only source to download',
                             )
argument_parser.add_argument('-i', '--input',
                             action='append',
                             help='add link',
                             required=True
                             )

argument_parser.add_argument('-q', '--quality',
                             action='store',
                             # default=2,
                             help=textwrap.dedent('''\
                                the higher the number the lower the quality.
                                mp4 format code :
                                no      format          desc
                                1: '299+140/298+140'    1080p60
                                2: '298+140',           720p60
                                3: '137+140/136+140',   1080p
                                4: '136+140/135+140',   720p
                                5: '135+140/134+140'    480p
                                webm format code:
                                1: '303+251/302+251',   1080p60
                                2: '302+251',           720p60
                                3: '248+251/247+251',   1080p
                                4: '247+251/244+251',   720p
                                5: '244+251/243+251'    480p
                                ''')
                             )
argument_parser.add_argument('-f', '--format',
                             action='store',
                             choices=video_source,
                             help='video source download %s' % video_source
                             )

argument_parser.add_argument('-np', '--no-playlist',
                             action='store_true',
                             help='download all playlist if entries'
                             )

argument_parser.add_argument('-o', '--output',
                             action='store',
                             help='output format'
                             )
argument_parser.add_argument('-c', '--codec',
                             action='store',
                             help='codec for output extension',
                             choices=audio_codec + video_codec
                             )
argument_parser.add_argument('-k', '--keep',
                             action='store_true',
                             help='not erase downloaded video'
                             )
argument_parser.add_argument('-d', '--downloader',
                             action='store',
                             help='aria2c, avconv, axel, curl, ffmpeg, httpie, wget'
                             )
argument_parser.add_argument('-t', '--threads',
                             action='store',
                             type=int,
                             help='multiple download when the link is entries or playlist',
                             default=2,
                             choices=range(2, 11)
                             )

parsed_arg = argument_parser.parse_args()

"""
parsing from argparse
-a	switch audio_only
-i 	is download url
-f	source to download for video. audio is default 251/140
-q	quality based youtube-dl see help
-np	no playlist. if playlist or entries download only one
-o	output template. see outtmp or config.ini
-c	codec for extension output format
-k	keep video. do not remove source after post processing
-d  Use the specified external downloader. Currently supports 
    aria2c, avconv, axel, curl, ffmpeg, httpie, wget
-t  number of threads to download.    

"""
audio_only = vars(parsed_arg).get('audio')
url = vars(parsed_arg).get('input')
src = vars(parsed_arg).get('format')
qua = vars(parsed_arg).get('quality')
np = vars(parsed_arg).get('no-playlist')
output = vars(parsed_arg).get('output')
codec = vars(parsed_arg).get('codec')
keep = vars(parsed_arg).get('keep')
exdl = vars(parsed_arg).get('downloader')
thread_nums = vars(parsed_arg).get('threads')

# total_url = len(url)

# init threading
pool = ActivePool()
semaphore = threading.Semaphore(thread_nums)

# set download destination by switch -o from argparse
if output == 'phone':
    destination = config.get('DESTINATION', 'phone') + '%(title)s.%(ext)s'
elif output == 'test':
    destination = config.get('DESTINATION', 'test') + '%(title)s.%(ext)s'
else:
    # perhaps requires destination checking
    if not output:
        destination = config.get('DESTINATION', 'test') + '%(title)s.%(ext)s'
    else:
        destination = output + '%(title)s.%(ext)s'

# once -a switch is true
if audio_only:
    if codec in audio_codec:
        logging.debug("output extension %s" % codec)
        pass
    else:
        logging.error("error selecting codec for audio, \
                       select from list bellow :")
        prompt_audio_codec = prompt(
            {
                'type': 'list',
                'name': 'codec',
                'message': 'known audio codec',
                'choices': audio_codec,
                'default': default_audio_codec
            }
        )
        codec = prompt_audio_codec['codec']

    audio_quality = default_audio_quality if not qua else qua

    ydl_opts = {
        'format': '251/140',
        'noplaylist': np,
        'outtmpl': destination,
        'keepvideo': keep,
        'external_downloader': exdl,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': audio_quality

            },
            {'key': 'FFmpegMetadata'},
        ],
    }


else:
    """
    TODO : Video Downloader

    - source format to download remainder 
        requires for no post processing
    
    - quality reminder
        to get format code to download 
    """

    # source format reminder
    if not src:
        src_prompt = prompt(
            {
                'type': 'list',
                'name': 'source',
                'message': 'source download %s' % video_source,
                'choices': video_source
            }
        )
        src = src_prompt['source']

    if not qua:
        quality_prompt = prompt(
            {
                'type': 'list',
                'name': 'quality',
                'message': '3xx is HQ 60 fps; 2xx is 30 fps',
                'choices': ['1080p60', '720p60', '1080p', '720p', '480p'],
                'default': '720p60',
            }
        )
        qua = pixel_to_quality(quality_prompt['quality'])

    qua = int(qua)
    video_source_format = quality(src, qua)
    # logging.debug('src: %s\nqua: %s\nvsrc: %s' % (src, qua, vsrc))

    ydl_opts = {
        'format': video_source_format,
        'noplaylist': np,
        'outtmpl': destination,
        'keepvideo': keep,
        'external_downloader': exdl,
    }

    # logging.debug('options %s' % ydl_opts)

for uri in url:
    # uri is string from list url. required to extract_info
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(uri, download=False)
        m_upload_date = meta['upload_date']
        m_uploader = meta['uploader']
        m_view_count = meta['view_count']
        m_like_count = meta['like_count']
        m_dislike_count = meta['dislike_count']
        m_id = meta['id']
        m_format = meta['format']
        m_duration = meta['duration']
        m_title = meta['title']
        m_description = meta['description']

    #     _title = meta['title']
        logging.debug(textwrap.dedent(
            '''
            upload_date     : %s
            uploader        : %s
            view_count      : %s
            like_count      : %s
            dislike_count   : %s
            id              : %s
            format          : %s
            duration        : %s
            title           : %s
            ''' % (m_upload_date, m_uploader, m_view_count,
                   m_like_count, m_dislike_count, m_id,
                   m_format, m_duration, m_title)))

    uri2list = [uri]
    threading.Thread(target=downloader, name=m_id,
                     args=(semaphore, pool, ydl_opts, uri2list)).start()

update_thread = threading.Thread(
    target=updater,
    name="updater",
    args=(semaphore, pool)
).start()

# download_thread.start()
# update_thread.start()

# sys.exit(1)


"""
    cheat sheet :

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info('https://youtu.be/SWsStfj33Zg', download=True)
            ydl.download(url)
    
    meta list :
    upload_date
    uploader
    view_count
    like_count
    dislike_count
    id
    format
    duration
    title
    description



def my_hook(d):
    if d['status'] == 'finished':
        logging.('Done downloading, now converting ...')


youtube_dl.YoutubeDL(
    {
        'format': download['profile'],
        # 'simulate': True,
        'verbose': True,
        'logger': MyLogger(),
    }
).download([links['url']])


if answers['dltype'] == 'audio':
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
"""
"""
    the higher the number the lower the quality, 1 is the best
    [mp4]: 299 1920x1080 1080p60 , avc1.64002a, 60fps
    [mp4]: 298 1280x720  720p60  , avc1.4d4020, 60fps
    [mp4]: 137 1920x1080 1080p   , avc1.640028, 30fps
    [mp4]: 136 1280x720  720p    , avc1.4d401f, 30fps
    [mp4]: 135 854x480   480p    , avc1.4d401f, 30fps
    [webm]: 303 1920x1080 1080p60 , vp9, 60fps
    [webm]: 302 1280x720  720p60  , vp9, 60fps
    [webm]: 248 1920x1080 1080p   , vp9, 30fps
    [webm]: 247 1280x720   720p   , vp9, 30fps
    [webm]: 244 854x480    480p   , vp9, 30fps
    weird codec
    [mp4]: 399 1920x1080  1080p60 , av01.0.09M.08, 60fps
    [mp4]: 398 1280x720   720p60  , av01.0.08M.08, 60fps
    [mp4]: 397 854x480    480p    , av01.0.04M.08, 30fps
    audio only
    [m4a] : 140 130k mp4a.40.2@128k (44100Hz)
    [m4a] : 139  50k mp4a.40.5@ 48k (22050Hz)
    [webm]: 251 142k     opus @160k (48000Hz)
    [webm]: 250  72k     opus @ 70k (48000Hz)
    [webm]: 249  55k     opus @ 50k (48000Hz)
    number 1    : 1080p60 + m4a  128k [mp4]
                : 1080p60 + opus 160k [webm]
    number 2    :  720p60 + m4a  128k [mp4]
                :  720p60 + opus 160k [webm]
    number 3    :   1080p + m4a  128k [mp4]
                :   1080p + opus 160k [webm]
    number 4    :    720p + m4a  128k [mp4]
                :    720p + opus 160k [webm]
    number 5    :    480p + m4a  128k [mp4]
                :    480p + opus 160k [webm]
    For audio :
    based from youtube-dl if preferred quality < 10, option q:a are used
    and else bitrate audio b:a are used. take a look approximately
    bit rate data above
    """
# URL test
# video
# 60 fps
# https://youtu.be/kA2PUGR6gAc
# https://youtu.be/AR3Fa-FQ-0A
# https://youtu.be/2AecAXinars

# audio
# https://youtu.be/SWsStfj33Zg
# https://youtu.be/QtONLUT8JHk
# https://youtu.be/ylAMEVTpRKM
# https://youtu.be/EFI47bWP_NI
# https://youtu.be/igxbB1-Q7Rs
# https://youtu.be/X7mGwS-DU8U
# https://youtu.be/0yLL7YcMt8Q

# playlist
# https://www.youtube.com/watch?v=QtONLUT8JHk&list=PLFVRTVtP12j3312mmQHoIbXchQlJYEJ5u
