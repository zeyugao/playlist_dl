# encoding=utf-8
# python3

import hashlib
import os

import mutagen
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, error
from mutagen.mp3 import MP3

progressbar_window = None


def download_music_file(url, file_path, file_name, file_md5=None, overwrite=False, retrytimes=3):
    '''
        下载音乐文件

    Args:
        file_path<str>:音乐文件的绝对路径
        file_md5<str>:网站上传下来的md5值
        overwrite<bool>:是否覆盖已经存在的文件
        retrytimes<int>:重试次数，仅在md5值不正确时尝试重试，其余情况直接报错
    '''
    if progressbar_window:
        progressbar_window.set_label_single_song_progress('Downloading file: %s' % file_name)
        progressbar_window.set_single_song_progress(0)
    if os.path.exists(file_path) and not overwrite:
        print('File: %s already exists, skip' % file_path)
        if progressbar_window:
            progressbar_window.set_single_song_progress(100)
        return
    if os.path.exists(file_path):
        os.remove(file_path)
    respond = requests.get(url, stream=True)
    file_lenght = int(respond.headers.get('content-length'))
    print('File size: %s B, %s KB' % (int(file_lenght), int(file_lenght / 1024)))
    current_file_md5 = hashlib.md5()
    with open(file_path, 'wb') as file:
        for chunk in respond.iter_content(chunk_size=1024):
            if chunk:
                if progressbar_window:
                    progressbar_window.step_single_song_progress(102400 / file_lenght)
                current_file_md5.update(chunk)
                file.write(chunk)
    if not file_md5:
        return
    if not str(current_file_md5.hexdigest()) == file_md5:
        print('File:%s.mp3 download failed, retry, %d times left' % file_path, retrytimes)
        if retrytimes > 0:
            download_music_file(url, file_path, file_md5, retrytimes - 1, True)
        else:
            print('File:%s.mp3 download failed' % file_path)
    else:
        print('MD5 check succeed')


def download_album_pic(url, file_path, overwrite=False):
    '''
        下载专辑封面

    Args:
        file_path<str>:音乐专辑的绝对路径
        overwrite<bool>:是否覆盖已经存在的文件
    '''

    if os.path.exists(file_path) and not overwrite:
        print('File: %s already exists, skip' % file_path)
        return
    if os.path.exists(file_path):
        os.remove(file_path)
    respond = requests.get(url)
    if respond.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(respond.content)


def modify_mp3(mp3_path, music_info):
    '''
    修改mp3文件的信息
    Args:
        mp3_path<str>:
            mp3文件的路径
        music_info<dict>:
            title<str>:标题
            artists<str>:作者
            album<str>:所属专辑
            pic_path<str>:专辑封面的路径
    '''
    print('Modify mp3 ID3 for song: %s' % music_info['file_name'])
    try:
        audiofile = EasyID3(mp3_path)
    except:
        audiofile = mutagen.File(mp3_path, easy=True)
        audiofile.add_tags()
    if 'artists' in music_info:  # and not 'artist' in audiofile:
        audiofile['artist'] = music_info['artists'].split(';')
        audiofile['albumartist'] = music_info['artists'].split(';')
    if 'title' in music_info:  # and not 'title' in audiofile:
        audiofile['title'] = music_info['title']
    if 'album' in music_info:  # and not 'album' in audiofile:
        audiofile['album'] = music_info['album']['name']
    if 'date' in music_info:  # and not 'date' in audiofile:
        audiofile['date'] = music_info['date']
    audiofile.save(v2_version=3)
    audiofile = ID3(mp3_path)
    if 'pic_path' in music_info:
        if os.path.exists(music_info['pic_path']):
            with open(music_info['pic_path'], 'rb') as pic_file:
                audiofile['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=pic_file.read())
    audiofile.save(v2_version=3)
