# encoding=utf-8
# python3
import eyed3

# TODO


def generate_163key(data):
    key = "#14ljk_!\]&0U<'("
    # AES 128
    pass


def modify_info(mp3_path, **kwargs):
    '''修改mp3文件的信息
    Args:
        mp3_path<str>:mp3文件的路径
        kwargs<dict>:
            title:标题
            artists:作者
            album:所属专辑
            pic_path:专辑封面的路径
    '''
    audiofile = eyed3.load(mp3_path)
    audiofile.initTag()
    if 'artists' in kwargs:
        audiofile.tag.artist = kwargs['artists']  # .decode('utf-8')
    if 'title' in kwargs:
        audiofile.tag.title = kwargs['title']  # .decode('utf-8')

    if 'album' in kwargs:
        audiofile.tag.album = kwargs['album']  # .decode('utf-8')

    if 'pic_path' in kwargs:
        # No check here
        with open(kwargs['pic_path'], 'rb') as pic_file:
            imagedata = pic_file.read()
            audiofile.tag.images.set(3, imagedata, 'image/jpeg', u'')
    if 'time' in kwargs:
        audiofile.tag.recording_date = kwargs['time']
    if 'company' in kwargs:
        audiofile.tag.publisher = kwargs['company']
    audiofile.tag.save()
