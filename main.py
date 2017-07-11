# encoding=utf-8
# python3
import netease
import getopt
import sys
import time
from mp3_modify import modify_info


def wait():
    print('Wait for 3s')
    time.sleep(3)  # 防止被网易ban


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', [''])
    except getopt.GetoptError as e:
        print(e)
        return

    netease_ins = netease.NetEase()
    ret_info, pack = netease_ins.get_and_parse_playlist_detail_weapi(args[0])
    print('')
    for (br, ids) in pack.items():
        wait()
        all_songs_info = netease_ins.get_songs_info_weapi(ids, br)
        for single_song_info in all_songs_info:
            current_song_info = ret_info[single_song_info['id']]
            song_download_url = None

            if single_song_info['url']:
                song_download_url = single_song_info['url']
            else:
                song_download_url = netease_ins.search_song(single_song_info['id'], current_song_info['file_name'])
            if song_download_url is None:
                print('Faild download song %s' % current_song_info['file_name'])
                continue
            file_path = netease_ins.download_single_song_and_save(
                song_download_url, current_song_info['file_name'])

            pic_path = netease_ins.download_album_pic_and_save(current_song_info['album']['picUrl'],
                                                               current_song_info['file_name'])
            print('Modify info for song: %s' % current_song_info['file_name'])
            modify_info(file_path, pic_path=pic_path, title=current_song_info[
                        'song_name'], album=current_song_info['album']['name'],
                        artists=current_song_info['artists'], time=current_song_info['year'],
                        company=current_song_info['company'])
            print('')
            wait()


if __name__ == '__main__':
    main()
