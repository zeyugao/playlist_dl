# encoding=utf-8
# python3
import netease
import getopt
import sys
import time
import tools

privilege = {
    1: 'h',
    0: 'm',
    2: 'l'
}
music_folder = './music_save/'
pic_folder = './pic_save/'


def wait(wait_time=1):
    print('Wait for %ds' % wait_time)
    time.sleep(wait_time)  # 防止被网易ban

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', [''])
    except getopt.GetoptError as e:
        print(e)
        return

    netease_ins = netease.NetEase()
    netease_ins.set_privilege_weapi(privilege)
    netease_ins.set_save_folder(music_folder=music_folder, pic_folder=pic_folder)

    song_info_sortby_id, playlist_detail_sortby_br = netease_ins.get_and_parse_playlist_detail_weapi(args[0])
    print('')
    for (br, ids) in playlist_detail_sortby_br.items():
        wait()
        all_songs_info = netease_ins.get_songs_info_weapi(ids, br)
        for single_song_info in all_songs_info:
            current_song_info = song_info_sortby_id[single_song_info['id']]
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
            current_song_info['pic_path'] = pic_path

            print('Modify info for song: %s' % current_song_info['file_name'])
            tools.modify_info(file_path, current_song_info)
            print('')
            wait()


if __name__ == '__main__':
    main()
