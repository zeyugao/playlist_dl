# encoding=utf-8
# python3

import base64
import binascii
import hashlib
import json
import hashlib
import os
import time

import requests
from Crypto.Cipher import AES

from tools import (download_music_file,download_album_pic,modify_mp3)

MODULUS = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
PUBKEY = '010001'
NONCE = b'0CoJUm6Qyw8W8jud'


def encrypted_id(id):
    magic = bytearray('3go8&$8*3*3h0k(2)2', 'u8')
    song_id = bytearray(id, 'u8')
    magic_len = len(magic)
    for i, sid in enumerate(song_id):
        song_id[i] = sid ^ magic[i % magic_len]
    m = hashlib.md5(song_id)
    result = m.digest()
    result = base64.b64encode(result).replace(b'/', b'_').replace(b'+', b'-')
    return result.decode('utf-8')


def encrypted_request(text):
    # type: (str) -> dict
    data = json.dumps(text).encode('utf-8')
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {'params': params, 'encSecKey': encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16),
             int(pubkey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


fake_headers = {
    # 'Cookie': 'appver=1.5.2',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com/search/',
    'X-Real-IP': '27.38.4.87',
    'Cookie':'os=ios',      # 不知道为什么加了这一句，就可以下载一些歌了
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36')
}

#  __remember_me=true;_iuqxldmzr_=32; appsign=true; websign=true; 


class NetEase(object):
    session = requests.Session()
    csrf = ''

    def __init__(self):
        self.privilege = {1: 'h', 0: 'm', 2: 'l'}

    def set_playlist_id(self, id):
        self.id = id

    def set_playlist_url(self, url):
        self.id = url.split('playlist?id=')[1]

    def get_playlist_detail(self, playlist_id):
        target_url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token=' + self.csrf
        data = {
            'id': self.id,
            'offset': 0,
            'total': 'true',
            'limit': 5000,
            'n': 5000,
            'csrf_token': self.csrf
        }
        ret_json = json.loads(self.session.post(target_url, data=encrypted_request(data), headers=fake_headers).text)
        if(ret_json['code'] == 200):
            return ret_json['playlist']['tracks']
        else:
            print('Error! Code: %s\n', ret_json['code'])
            return ret_json['data']

    def get_quality_by_privilege(self, all_quality):
        '''
            根据原先设置的优先级确定某一首歌曲的码率
        '''
        selected_quality = -1
        for current_br in range(0, len(self.privilege)):
            if all_quality[self.privilege[current_br]]:
                selected_quality = self.privilege[current_br]
                break
        return selected_quality

    def replace_file_name(self, file_name):
        t = ["\\", "/", "*", "?", "<", ">", "|", '"']
        for i in t:
            file_name = file_name.replace(i, '')
        return file_name

    def parse_playlist_detail(self, origin_playlist_detial):
        if origin_playlist_detial is None:
            return {}, {}
        self.songs_detail = {}
        self.download_music_info = {}
        for origin_single_song_detail in origin_playlist_detial:
            single_song_detail = {}
            single_song_detail['title'] = origin_single_song_detail['name']
            single_song_detail['album'] = {}
            single_song_detail['artists'] = ''
            for artist in origin_single_song_detail['ar']:
                single_song_detail['artists'] = single_song_detail['artists'] + artist['name'] + ','
            single_song_detail['artists'] = single_song_detail['artists'][:-1]
            if len(single_song_detail['artists']) > 50:
                # 如果艺术家过多导致文件名过长，则文件名的作者则为第一个艺术家的名字
                print('Song: %s\'s name too long, cut' % single_song_detail['title'])
                single_song_detail['file_name'] = single_song_detail['artists'].split(',')[0] + ' - ' + single_song_detail['title']
            else:
                single_song_detail['file_name'] = single_song_detail['artists'] + ' - ' + single_song_detail['title']
            single_song_detail['artists'] = single_song_detail['artists'].replace(',', ';')
            single_song_detail['file_name'] = self.replace_file_name(single_song_detail['file_name'])
            single_song_detail['id'] = origin_single_song_detail['id']
            if 'al' in origin_single_song_detail and origin_single_song_detail['al']:
                single_song_detail['album']['picUrl'] = origin_single_song_detail['al']['picUrl']
                single_song_detail['album']['name'] = origin_single_song_detail['al']['name']
            quality = {}
            quality['h'] = origin_single_song_detail['h']['br'] if origin_single_song_detail['h'] else None  # high
            quality['m'] = origin_single_song_detail['m']['br'] if origin_single_song_detail['m'] else None  # middle
            quality['l'] = origin_single_song_detail['l']['br'] if origin_single_song_detail['l'] else None  # low
            quality_id = origin_single_song_detail[self.get_quality_by_privilege(quality)]['br']
            if quality_id in self.download_music_info:
                self.download_music_info[quality_id].append(origin_single_song_detail['id'])
            else:
                self.download_music_info[quality_id] = [origin_single_song_detail['id']]
            self.songs_detail[single_song_detail['id']] = single_song_detail

    def get_songs_info(self):
        target_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token=' + self.csrf
        error_song_ids = []
        for (br, ids) in self.download_music_info.items():
            data = {
                'ids': ids,
                'br': br,
                'csrf_token': self.csrf
            }

            json_ret = json.loads(self.session.post(target_url, data=encrypted_request(data), headers=fake_headers).text)
            if json_ret['code'] == 200:
                # print(json_ret)
                json_ret = json_ret['data']
            else:
                print('Error! Code: %s' % json_ret['code'])
                error_song_ids.append(ids)
                continue
            for single_song_detail in json_ret:
                # print(single_song_detail['url'])
                if single_song_detail['url']:
                    self.songs_detail[single_song_detail['id']]['url'] = single_song_detail['url']
                    self.songs_detail[single_song_detail['id']]['md5'] = single_song_detail['md5']
                else:
                    error_song_ids.append(single_song_detail['id'])
        return error_song_ids

    def download_music(self, music_folder, pic_folder, retrytimes):
        for id in self.songs_detail:
            single_song_detail = self.songs_detail[id]
            # print(single_song_detail['url'])
            file_path = None
            if single_song_detail['url']:
                file_path = os.path.join(music_folder, single_song_detail['file_name'] + '.mp3')
                print('Donwload song file: %s' % single_song_detail['file_name'])
                download_music_file(single_song_detail['url'],
                                         file_path,
                                         file_md5 = single_song_detail['md5'],
                                         retrytimes=retrytimes)
            if single_song_detail['album']['picUrl']:
                pic_path = os.path.join(pic_folder, single_song_detail['file_name'] + '.jpg')
                download_album_pic(single_song_detail['album']['picUrl'], pic_path)
            modify_mp3(file_path, single_song_detail)

    def download_playlist(self, music_folder, pic_folder, retrytimes=3):
        origin_playlist_detial = self.get_playlist_detail(self.id)
        self.parse_playlist_detail(origin_playlist_detial)

        error_songs_ids = self.get_songs_info()

        error_songs_ids = self.get_songs_detail_old_api(error_songs_ids)

        for id, d in self.songs_detail.items():
            try:
                d['url']
            except:
                print(id, d['title'])
        self.download_music(music_folder, pic_folder, retrytimes)

        error_songs_detail = []

        for single_error_song_id in error_songs_ids:
            error_songs_detail.append(self.songs_detail[single_error_song_id])
        return error_songs_detail

    def get_songs_detail_old_api(self, songs_id):
        target_url = 'http://music.163.com/weapi/search/pc'

        # TODO:提供品质的选择
        quality_privilege = {1: 'mMusic', 0: 'hMusic', 2: 'lMusic', 3: 'bMusic'}
        error_songs_ids = []
        for song_id in songs_id:
            data = {
                's': str(song_id),
                'limit': 1,
                'type': 1,
                'offset': 0,
            }
            try:
                json_ret = json.loads(self.session.post(target_url, data=encrypted_request(data),
                                                        headers=fake_headers).text)['result']['songs'][0]
            except IndexError:
                print("Can't get song")
                error_songs_ids.append(song_id)
            music = {}
            for i in range(0, len(quality_privilege)):
                if json_ret[quality_privilege[i]]:
                    music = json_ret[quality_privilege[i]]
                    break
            url = None
            if 'dfsId' in music:
                dfsId = music['dfsId']
            if 'dfsId_str' in music:
                dfsId = music['dfsId_str']
            if music and dfsId:
                url = 'http://p2.music.126.net/%s/%s.jpg.mp3' % (encrypted_id(str(dfsId)), dfsId)
            elif not json_ret['mp3Url'].endswith('==/0.mp3'):
                url = json_ret['mp3Url']
            else:
                error_songs_ids.append(song_id)
                continue
            self.songs_detail[song_id]['url'] = url

        return error_songs_ids

    def try_again(self):
        target_url = 'http://music.163.com/weapi/song/enhance/player/url'
        data = {
            'ids': [536623441],
            'br': 999000
        }
        fake_headers = {
            # 'Cookie': 'appver=1.5.2',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'X-Real-IP': '27.38.4.87',
            
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36')
        }
        
        json_ret = json.loads(self.session.post(target_url, data=encrypted_request(data), headers=fake_headers).text)
        print(json_ret)
