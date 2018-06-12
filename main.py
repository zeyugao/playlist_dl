# encoding=utf-8
# python3
from netease import NetEase
import search
import getopt
import sys
import os


def read_extra_music(extra_music_file):
    if not os.path.exists(extra_music_file):
        return []
    extra_music = []
    with open(extra_music_file, 'r') as file:
        for line in file:
            splited_line = line.split(' ')
            extra_music.append({
                'title': splited_line[0],
                'artists': splited_line[1],
                'album': splited_line[2],
                'type': splited_line[3]
            })


def download_playist(playlist_url,
                     music_folder='./music_save/',
                     pic_folder='./pic_save/',
                     privilege={1: 'h', 0: 'm', 2: 'l'}):
    # 检查目录
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)

    search_songs_list = []
    '''
    ne = NetEase()
    ne.set_playlist_url(playlist_url)
    error_songs_detail = ne.download_playlist(music_folder=music_folder, pic_folder=pic_folder)

    for error_song in error_songs_detail:
        search_songs_list.append({
            'title': error_song['title'],
            'artists': error_song['artists'].replace(';', ' '),
            'album': error_song['album']['name'],
            'type': 'qq'
        })
    '''

    search_songs_list.extend(read_extra_music(os.path.join(os.getcwd(),'extra_music_file.txt')))

    s = search.Sonimei()
    for single_song in search_songs_list:
        s.download_song(single_song['title'], single_song['artists'], single_song['album'], music_folder, pic_folder, single_song['type'])


def main():
    try:
        args = getopt.getopt(sys.argv[1:], '', [''])[1]
    except getopt.GetoptError as e:
        print(e)
        return
    download_playist(args[0])


if __name__ == '__main__':
    main()
