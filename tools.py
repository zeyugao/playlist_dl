# encoding=utf-8
# python3
import eyed3

# TODO


def generate_163key(data):
    key = "#14ljk_!\]&0U<'("
    # AES 128
    pass


def modify_info(mp3_path, custom_info):
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
    if 'artists' in custom_info:
        audiofile.tag.artist = custom_info['artists']  # .decode('utf-8')
    if 'title' in custom_info:
        audiofile.tag.title = custom_info['title']  # .decode('utf-8')

    if 'album' in custom_info:
        audiofile.tag.album = custom_info['album']['name']  # .decode('utf-8')

    if 'pic_path' in custom_info:
        # No check here
        with open(custom_info['pic_path'], 'rb') as pic_file:
            imagedata = pic_file.read()
            audiofile.tag.images.set(3, imagedata, 'image/jpeg', u'')
    if 'time' in custom_info:
        audiofile.tag.recording_date = custom_info['time']
    if 'company' in custom_info:
        audiofile.tag.publisher = custom_info['company']
    audiofile.tag.save()
