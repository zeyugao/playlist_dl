# encoding=utf-8
# python3
import os

from . import search
from . import tools
from .netease import NetEase
from . import configuration

ne = NetEase()


def read_extra_music(extra_music_file):
    if not os.path.exists(extra_music_file):
        return []
    extra_music = []
    with open(extra_music_file, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.startswith('#'):
                continue
            splited_line = line.split(';')
            extra_music.append({
                'title': splited_line[0],
                'artists': splited_line[1],
                'album': splited_line[2],
                'type': splited_line[3].replace('\n', '')
            })
    return extra_music


def download_songs_via_searching(songs_detail, music_folder, pic_folder, extra_music_file=None):
    if tools.progressbar_window:
        tools.progressbar_window.set_label_searching_song()

    search_songs_list = []

    if not extra_music_file:
        extra_music_file = configuration.config.get_config('extra_music_file')
    search_songs_list.extend(read_extra_music(extra_music_file))
    extra_music_folder = os.path.join(configuration.config.get_config('music_folder'), 'extra_music')
    if not os.path.exists(extra_music_folder):
        os.makedirs(extra_music_folder)

    extra_pic_folder = os.path.join(configuration.config.get_config('pic_folder'), 'extra_music')
    if not os.path.exists(extra_pic_folder):
        os.makedirs(extra_pic_folder)
    new_error_song = []
    s = search.Sonimei()

    current_song_index = 0
    for single_song in search_songs_list:
        current_song_index += 1
        if tools.progressbar_window:
            tools.progressbar_window.set_label_single_song_progress('Searching music: %s - %s' % (single_song['artists'], single_song['title']))
            tools.progressbar_window.set_single_song_progress(0)
            tools.progressbar_window.set_playlist_progress(current_song_index, len(search_songs_list))
        if not s.download_song(single_song['title'], single_song['artists'], single_song['album'], extra_music_folder, extra_pic_folder, single_song['type']):
            new_error_song.append(single_song['artists'] + ' - ' + single_song['title'])
    return new_error_song


def download_netease_playist(playlist,
                             music_folder,
                             pic_folder,
                             privilege={1: 'h', 0: 'm', 2: 'l'}):
    '''
        下载歌单
    Args:
        playlist<str>:歌单的url或者id
        music_folder<str>:文件夹，用于存下载的歌曲
        pic_folder<str>:文件夹，用于存下载的歌曲的专辑封面
        extra_music_file<str>:文件，加入额外的音乐
        privilege<dict>:优先级
    '''
    # 检查目录
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)

    if playlist.isdigit():
        ne.set_playlist_id(playlist)
    else:
        ne.set_playlist_url(playlist)
    error_songs_detail = ne.download_playlist(music_folder=music_folder, pic_folder=pic_folder)
    error_songs_list = []
    for error_song in error_songs_detail:
        error_songs_list.append({
            'title': error_song['title'],
            'artists': error_song['artists'].replace(';', ' '),
            'album': error_song['album']['name'],
            'type': 'qq'
        })
    return error_songs_list
