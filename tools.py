# encoding=utf-8
# python3

import hashlib
import os

import eyed3
import requests


def download_music_file(url, file_path, file_md5 = None, overwrite=False, retrytimes=3):
    '''
        下载音乐文件

    Args:
        file_path<str>:音乐文件的绝对路径
        file_md5<str>:网站上传下来的md5值
        overwrite<bool>:是否覆盖已经存在的文件
        retrytimes<int>:重试次数，仅在md5值不正确时尝试重试，其余情况直接报错
    '''
    if os.path.exists(file_path) and not overwrite:
        print('File: %s already exists, skip' % file_path)
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
    audiofile = eyed3.load(mp3_path)
    audiofile.initTag()
    if 'artists' in music_info and not audiofile.tag.artist:
        audiofile.tag.artist = music_info['artists']
    if 'title' in music_info and not audiofile.tag.title:
        audiofile.tag.title = music_info['title']
    if 'album' in music_info and not audiofile.tag.album:
        audiofile.tag.album = music_info['album']['name']
    if 'pic_path' in music_info:
        if os.path.exists(music_info['pic_path']):
            with open(music_info['pic_path'], 'rb') as pic_file:
                imagedata = pic_file.read()
                audiofile.tag.images.set(3, imagedata, 'image/jpeg', u'')
    if 'time' in music_info and not audiofile.tag.publisher:
        audiofile.tag.recording_date = music_info['time']
    if 'company' in music_info and not audiofile.tag.publisher:
        audiofile.tag.publisher = music_info['company']
    audiofile.tag.save()
