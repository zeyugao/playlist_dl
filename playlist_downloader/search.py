# encoding=utf-8
# python3

import json
import os

import requests
import difflib

from .tools import download_album_pic, download_music_file, modify_mp3


class Sonimei(object):
    def download_song(self, song_title, song_author, song_album, music_folder, pic_folder, type):
        '''
            在music.sonimei.cn上搜索歌曲，并下载

        Args:
            song_title<str>:歌曲名
            song_author<str>:歌手名
            song_album<str>:专辑名
            music_folder<str>:相对于程序目录的文件夹，用于存下载的歌曲
            pic_folder<str>:相对于程序目录的文件夹，用于存下载的歌曲的专辑封面
            type<str>:用于传递到music.sonimei.cn，用来设置从哪个音乐网站上搜索
                <可选参数>: kugou   netease qq
                            kuwo    xiami   baidu
                            1ting   migu    lizhi
                            qingting    ximalaya
                            kg      5singyc 5singfc
        '''

        search_result = self.search(song_title, song_author, type)
        if search_result is None:
            return False
        del search_result['lrc']

        artists = search_result['author'].split(',')
        file_name = ''
        for artist in search_result['author'].split(','):
            file_name = file_name + artist + ','
        file_name = file_name[:-1]
        if len(file_name) > 50:
            # 如果艺术家过多导致文件名过长，则文件名的作者则为第一个艺术家的名字
            print('Song: %s\'s name too long, cut' % search_result['title'])
            file_name = artists[0] + ' - ' + search_result['title']
        else:
            file_name = file_name + ' - ' + search_result['title']
        file_path = os.path.join(music_folder, file_name + '.mp3')
        pic_path = os.path.join(pic_folder, file_name + '.jpg')
        try:
            download_music_file(search_result['url'], file_path=file_path, file_name=(file_name + '.mp3'))
        except AssertionError:
            return False
        except FileExistsError:
            pass
        else:
            download_album_pic(search_result['pic'], pic_path)
            music_info = {
                'title': search_result['title'],
                'artists': search_result['author'].replace(',', ';'),
                'pic_path': pic_path,
                'file_name': file_name
            }
            if song_album and not song_album == '':
                music_info['album'] = {}
                music_info['album']['name'] = song_album
            modify_mp3(file_path, music_info)
        return True

    def best_match(self, song_title, song_author, all_songs_detail):
        highest_ratio = 0
        highest_index = 0
        index = 0
        for song_detail in all_songs_detail:
            ratio_title = difflib.SequenceMatcher(None, song_title, song_detail['title']).ratio() * 100
            ratio_author = difflib.SequenceMatcher(None, song_author, song_detail['author']).ratio() * 100
            if ratio_author * ratio_title > highest_ratio:
                highest_ratio = ratio_author * ratio_title
                highest_index = index

                # 完全匹配，而且在搜索中优先级比其他的高，直接跳出了
                if highest_ratio == 100 * 100:
                    return song_detail
            index += 1
        return all_songs_detail[highest_index]

    def search(self, song_title, song_author, type, retrytimes=3):
        target_url = 'http://music.sonimei.cn/'
        fake_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                           ' (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'),
            # 'Referer': 'http://music.sonimei.cn/?name=%s%s&type=%s',  # % (song_title, song_author, type),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://music.sonimei.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': 'music.sonimei.cn'
        }
        json_ret = None
        data = {
            'input': song_title + ' ' + song_author,
            'filter': 'name',
            'type': type,
            'page': 1
        }
        while retrytimes > 0:
            try:
                response = requests.post(target_url, data=data, headers=fake_headers)
                response.encoding = 'utf-8'
                json_ret = json.loads(response.text)
                if json_ret['code'] == 200:
                    return self.best_match(song_title, song_author, json_ret['data'])
                retrytimes = retrytimes - 1
            except IndexError:
                retrytimes = retrytimes - 1
        print('Download failed, song: %s - %s' % (song_author, song_title))
        return None


def xiami_search(song_title, song_author, retrytimes=3):
    # TODO
    # 暂时不知道怎么把虾米的api本地化，没有找到可行的Python参考项目
    target_url = 'http://music-api-jwzcyzizya.now.sh/api/search/song/xiami?&limit=1&page=1&key=%s-%s/' % (song_title, song_author)

    fake_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    json_ret = None
    while retrytimes > 0:
        try:
            json_ret = json.loads(requests.get(target_url, headers=fake_headers).text)
            break
        except:
            retrytimes = retrytimes - 1
    print(json_ret)
    if json_ret and json_ret['success']:
        return json_ret['songList'][0]['file']
    else:
        return ''
