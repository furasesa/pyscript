

class ContextManager:
    def __init__(self, dct):
        self.info_dict = dct
        self.formats = dct.get('formats', [dct])

    # def format_resolution(self, default='unknown'):
    #     if self.formats.get('vcodec') == 'none':
    #         return 'audio only'
    #     if self.formats.get('resolution') is not None:
    #         return format['resolution']
    #     if self.formats.get('height') is not None:
    #         if self.formats.get('width') is not None:
    #             res = '%sx%s' % (self.formats['width'], self.formats['height'])
    #         else:
    #             res = '%sp' % format['height']
    #     elif format.get('width') is not None:
    #         res = '%dx?' % format['width']
    #     else:
    #         res = default
    #     return res

    def get_codec_type(self):
        if self.formats.get('vcodec') == 'none':
            return 'audio only'
        else:
            if self.formats.get('acodec') is not None:
                if self.formats['acodec'] == 'none':
                    return 'video only'




# formats = mdict.get('formats', [mdict])
# table = [
#     [ydl.YoutubeDL.format_resolution(f), f['format_id'], f['ext'], format_note(f)]
#     for f in formats
#     if f.get('preference') is None or f['preference'] >= -1000]
# # logging.debug(formats)
# for t in table:
#     print(t)
