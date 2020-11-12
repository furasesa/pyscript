import logging


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
    def __init__(self, dct):
        self.info_dict = dct
        self.formats = dct.get('formats', [dct])
        self.result = []
        self.all_result = []
        self.filter_builder()
        self.raw_builder()

    def get_filtered_context(self):
        return self.result

    def get_raw_context(self):
        return self.all_result

    def raw_builder(self):
        def get_codec_type(format_dict,):
            if format_dict.get('vcodec') == 'none':
                return 'audio_only'
            elif format_dict.get('acodec') == 'none':
                return 'video_only'
            else:
                return 'av'

        for fmt in self.formats:
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
                specific = '%s + %s' % (video_spec, audio_spec)
            elif audio_spec is None:
                # video only
                specific = '%s' % video_spec
            elif video_spec is None:
                # audio only
                specific = '%s' % audio_spec
            else:
                # not supported
                specific = None

            self.all_result.append((
                format_id,
                '{:6} {}'.format(ext, specific)
            ))

        # logging.info(self.all_result)

    def filter_builder(self):
        global webm_audio_spec
        global m4a_spec
        for fmt in self.formats:
            format_id = fmt['format_id']
            ext = fmt['ext']

            '''
            audio only format_id 139 140 = m4a; 251 webm
            
            360p30  243 webm; 134 mp4
            480p30  244 webm; 135 mp4
            720p30  247 webm; 136 mp4
            720p60  302 webm; 298 mp4
            1080p60 303 webm; 299 mp4
            
            360p30  13  mp4
            720p30  22  mp4
            '''
            # initialize audio id for mp4 video
            if int(format_id) == 140:
                m4a_spec = get_audio_specific(fmt)
                logging.info('%s\t%s' % (format_id, m4a_spec))

            if int(format_id) == 251:
                webm_audio_spec = get_audio_specific(fmt)
                logging.info('%s\t%s' % (format_id, webm_audio_spec))

            # webm video
            if int(format_id) in range(243, 247, 1):
                video_spec = get_video_specific(fmt)
                if webm_audio_spec is not None:
                    audio_spec = webm_audio_spec
                    self.result.append((
                        '%s+251' % format_id,
                        '{:6}{}{}'.format(ext, video_spec, audio_spec)
                    ))

            if int(format_id) in range(134, 136, 1):
                video_spec = get_video_specific(fmt)
                if m4a_spec is not None:
                    audio_spec = m4a_spec
                    self.result.append((
                        '%s+140' % format_id,
                        '{:6}{}{}'.format(ext, video_spec, audio_spec)
                    ))

        # logging.info(self.result)



# formats = mdict.get('formats', [mdict])
# table = [
#     [ydl.YoutubeDL.format_resolution(f), f['format_id'], f['ext'], format_note(f)]
#     for f in formats
#     if f.get('preference') is None or f['preference'] >= -1000]
# # logging.debug(formats)
# for t in table:
#     print(t)
