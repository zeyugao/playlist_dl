# encoding=utf-8
# python3
import netease
import getopt
import sys
from mp3_modify import modify_info


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', [''])
    except getopt.GetoptError as e:
        print(e)
        return

    netease_ins = netease.NetEase()
    ret_info, pack = netease_ins.get_and_parse_playlist_detail_weapi(args[0])
    for (br, id_) in pack.items():
        all_songs_info = netease_ins.get_songs_info_weapi(pack[br], br)
        for single_song_info in all_songs_info:
            current_song_info = ret_info[single_song_info['id']]
            file_path = netease_ins.download_single_song_and_save(
                single_song_info['url'], current_song_info['file_name'])
            pic_path = netease_ins.download_album_pic_and_save(current_song_info['album']['picUrl'],
                                                               current_song_info['file_name'])
            print('Modify info for song: %s' % current_song_info['file_name'])
            modify_info(file_path, pic_path=pic_path, title=current_song_info[
                        'song_name'], album=current_song_info['album']['name'],
                        artists=current_song_info['artists'])


if __name__ == '__main__':
    main()
