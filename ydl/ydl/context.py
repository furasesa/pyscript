import logging
import youtube_dl


def get_value(format_dict, key):
    if format_dict.get(key) is not None:
        logging.debug('%s: %s' % (key, format_dict.get(key)))
        return format_dict.get(key)
    else:
        logging.error('%s is not found' % key)


def get_audio_specific(format_dict):
    acodec = get_value(format_dict, 'acodec')
    abr = get_value(format_dict, 'abr')
    asr = get_value(format_dict, 'asr')
    return '{}@{:<6}{}'.format(abr, asr, acodec)


def get_video_specific(format_dict):
    height = get_value(format_dict, 'height')
    width = get_value(format_dict, 'width')
    fps = get_value(format_dict, 'fps')
    # vbr = self.get_value(format_dict, 'vbr')
    vcodec = get_value(format_dict, 'vcodec')
    if int(width) > int(height):
        video_quality = '{}p'.format(height)
    else:
        video_quality = '{}p'.format(width)

    if width is not None and height is not None:
        resolution = '{}x{}'.format(width, height)
    else:
        resolution = get_value(format_dict, 'resolution')

    return '{}{:<4}{:5.4}{:10}'.format(video_quality, fps, vcodec, resolution)


class ContextManager:
    def __init__(self):
        # self.formats = None
        self.info_list = []
        self.all_formats = []
        self.video_formats = []
        self.audio_formats = []
        self.webm_video_list = ['243', '244', '245', '246', '247', '248', '301', '302', '303', '304', '305']
        self.mp4_video_list = ['134', '135', '136', '137', '297', '298', '299', '397', '398', '399']
        self.va_list = ['18', '22']
        # self.format_list = []
        # self.combined_result = []
        # self.all_result = []
        # self.audio_only_format = []

    def get_webm_video_list(self):
        return self.webm_video_list

    def get_mp4_video_list(self):
        return self.mp4_video_list

    def get_va_list(self):
        return self.va_list

    def generate_info(self, url):
        try:
            for uri in url:
                info_pack = {}
                json_info = youtube_dl.YoutubeDL({'forcejson': True}).extract_info(uri, download=False)
                # self.format_list.append((uri, info.get('formats', [info])))

                # [({'url': link}, {id: id}, {formats: fmt})]
                video_id = json_info.get('id')
                uploader = json_info.get('uploader')
                title = json_info.get('title')
                upload_date = json_info.get('uploade_date')
                description = json_info.get('description')
                categories = json_info.get('categories')
                duration = json_info.get('duration')
                webpage_url = json_info.get('webpage_url')
                if webpage_url is None:
                    webpage_url = uri
                view_count = json_info.get('view_count')
                average_rating = json_info.get('average_rating')
                formats = json_info.get('formats')

                info_pack.update({
                    'video_id': video_id,
                    'uploader': uploader,
                    'title': title,
                    'upload_date': upload_date,
                    'description': description,
                    'categories': categories,
                    'duration': duration,
                    'webpage_url': webpage_url,
                    'view_count': view_count,
                    'average_rating': average_rating,
                    'formats': formats
                })
                # print('info pack\n', info_pack, '\n\n')
                self.info_list.append(info_pack)
                self.all_formats_builder(title, webpage_url, formats)
                self.filtered_builder(title, webpage_url, formats)

        except youtube_dl.DownloadError as e:
            logging.error('{}', e)

    def print_info_list(self):
        for info in self.info_list:
            print('\n\n', info, '\n\n')

    def print_all_format(self):
        for info in self.all_formats:
            print('\n\n', info, '\n\n')

    #
    # def get_filtered_context(self):
    #     return self.combined_result
    #
    def get_all_formats(self):
        return self.all_formats

    def get_video_formats(self):
        return self.video_formats

    def get_audio_formats(self):
        return self.audio_formats
    #
    # def get_audio_only_context(self):
    #     return self.audio_only_format

    def all_formats_builder(self, title, url, formats):
        all_format_pack = {}
        format_selector = []

        def get_codec_type(format_dict,):
            if format_dict.get('vcodec') == 'none':
                return 'audio_only'
            elif format_dict.get('acodec') == 'none':
                return 'video_only'
            else:
                return 'av'

        for fmt in formats:
            format_id = fmt['format_id']
            ext = fmt['ext']
            codec_type = get_codec_type(fmt)
            video_spec = None
            audio_spec = None
            if codec_type == 'av':
                video_spec = get_video_specific(fmt)
                audio_spec = get_audio_specific(fmt)
            elif codec_type == 'audio_only':
                audio_spec = get_audio_specific(fmt)
            elif codec_type == 'video_only':
                video_spec = get_video_specific(fmt)
            else:
                logging.error('unknown type')

            if video_spec is not None and audio_spec is not None:
                # av
                specific = '{} + {}'.format(video_spec, audio_spec)
            elif audio_spec is None:
                # video only
                specific = '{}'.format(video_spec)
            elif video_spec is None:
                # audio only
                specific = '{}'.format(audio_spec)
            else:
                # not supported
                specific = None

            format_selector.append((format_id, '{:6} {}'.format(ext, specific)))

        # title, url, format_selector = tuple
        all_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': format_selector
        })

        self.all_formats.append(all_format_pack)
        logging.debug(self.all_formats)

        # logging.info(self.all_result)

    def filtered_builder(self, title, url, formats):
        global webm_audio_spec
        global m4a_spec

        audio_format_pack = {}
        video_format_pack = {}
        video_selector_list = []
        audio_selector_list = []

        for fmt in formats:
            format_id = fmt['format_id']
            ext = fmt['ext']
            # initialize audio id for mp4 video
            if format_id == '140':
                m4a_spec = get_audio_specific(fmt)
                audio_selector_list.append((format_id, '{:6} {}'.format(ext, m4a_spec)))

            if format_id == '251':
                webm_audio_spec = get_audio_specific(fmt)
                audio_selector_list.append((format_id, '{:6} {}'.format(ext, webm_audio_spec)))

            # webm video
            if format_id in self.webm_video_list:
                logging.debug('\nformat id: {}'.format(format_id))
                video_spec = get_video_specific(fmt)
                if webm_audio_spec is not None:
                    audio_spec = webm_audio_spec
                    video_selector_list.append(('%s+251' % format_id, '{:6}{}{}'.format(ext, video_spec, audio_spec)))

            # mp4 video
            if format_id in self.mp4_video_list:
                logging.debug('\nformat id: {}'.format(format_id))
                video_spec = get_video_specific(fmt)
                if m4a_spec is not None:
                    audio_spec = m4a_spec
                    video_selector_list.append(('%s+140' % format_id, '{:6}{}{}'.format(ext, video_spec, audio_spec)))

        audio_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': audio_selector_list
        })
        video_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': video_selector_list
        })
        self.audio_formats.append(audio_format_pack)
        self.video_formats.append(video_format_pack)

        # logging.info(self.result)

# formats = mdict.get('formats', [mdict])
# table = [
#     [ydl.YoutubeDL.format_resolution(f), f['format_id'], f['ext'], format_note(f)]
#     for f in formats
#     if f.get('preference') is None or f['preference'] >= -1000]
# # logging.debug(formats)
# for t in table:
#     print(t)
