# encoding=utf-8
import requests
import json
import hashlib
import base64
import datetime
import os
import random
import binascii
import re
from Crypto.Cipher import AES
from http.cookiejar import LWPCookieJar

from storage import Storage

modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'
cookie_path = './cookie'

# 登录加密算法, 基于https://github.com/stkevintan/nw_musicbox脚本实现


def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {'params': encText, 'encSecKey': encSecKey}
    return data


def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return binascii.hexlify(os.urandom(size))[:16]


class NetEase(object):
    '''包装网易云的api'''

    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent':
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
        }
        self.session = requests.Session()
        self.storage = Storage()
        self.session.cookies = LWPCookieJar(cookie_path)
        self.session.cookies.load()
        self.csrf = ''
        for cookie in self.session.cookies:
            if cookie.name == '__csrf':
                self.csrf = cookie.value
        if self.csrf == '':
            print('Please update your cookie')
        self.set_privilege()
        self.set_save_folder()

    def login(self, username, password):
        pattern = re.compile(r'^0\d{2,3}\d{7,8}$|^1[34578]\d{9}$')
        if pattern.match(username):
            '''需要用手机登陆'''
            pass
        self.session.cookies.load()
        target_url = 'https://music.163.com/weapi/login?csrf_token='
        text = {
            'username': username,
            'password': password,
            'rememberLogin': 'true',
        }
        data = encrypted_request(text)
        try:
            ret = self.session.post(target_url, headers=self.headers, data=data)
            self.session.cookies.save()
            ret.encoding = 'utf-8'
            return ret.text
        except:
            return {'code': 501}

    def set_save_folder(self, music_folder='./music_save/', pic_folder='./pic_save/'):
        '''设置保存的音乐位置
           默认为脚本的执行同目录下的music_save文件夹
        '''
        self.pic_folder = pic_folder
        self.music_folder = music_folder
        if not os.path.exists(self.music_folder):
            os.makedirs(self.music_folder)
        if not os.path.exists(self.pic_folder):
            os.makedirs(self.pic_folder)

    def set_privilege(self, privilege_br=None):
        '''设置下载码率优先级
        Args:
            privilege_br<dict>:
            eg:
                privilege_br = {
                    0: 'h',  # high quality, fisrt
                    1: 'm',  # middle quality, second
                    2: 'l'   # low quality, third
                }
            如果该项为None或者不填，则为默认的码率，依次为m,h,l
            Warning & TODO:
                未对参数进行检查
        '''
        self.privilege = {}
        if privilege_br is None:
            self.privilege = {
                1: 'h',
                0: 'm',
                2: 'l'
            }
        else:
            self.privilege = privilege_br

    def download_file(self, url, file_path, overwrite=False):
        if os.path.exists(file_path) and not overwrite:
            return
        if os.path.exists(file_path):
            os.remove(file_path)

        respond = self.session.get(url, stream=True)
        file_lenght = int(respond.headers.get('content-length'))
        print('File size: %s KB' % int(file_lenght / 1024))
        with open(file_path, 'wb') as file:
            for chunk in respond.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    def download_album_pic_and_save(self, url, file_name):
        pic_path = os.path.join(self.pic_folder, file_name + '.jpg')
        print('Download album pic: %s' % file_name)
        self.download_file(url, pic_path)
        return pic_path

    def download_single_song_and_save(self, url, file_name):
        file_path = os.path.join(self.music_folder, file_name + '.mp3')
        print('Download song: %s' % file_name)
        self.download_file(url, file_path)
        return file_path

    def get_songs_info_weapi(self, songs_id, quality):
        target_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token=' + self.csrf

        data = {
            'ids': songs_id,
            'br': quality,
            'csrf_token': self.csrf
        }
        ret = self.session.post(target_url, data=encrypted_request(data), headers=self.headers)
        return json.loads(ret.text)

    def get_playlist_detail_weapi(self, playlist_id=None, playlist_url=None):
        '''用新版的weapi获取歌单信息
        Args:
            playlist_url:歌单网站
            playlist_id:歌单id
            二选一即可
        Ret:
            json:歌单信息

        '''
        id = None
        if not playlist_url and not playlist_id:
            raise ValueError('Need url or id')
        elif playlist_url and playlist_id:
            id = playlist_id
        elif playlist_id:
            id = playlist_id
        else:
            id = playlist_url.split('playlist?id=')[1]
        target_url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token=' + self.csrf
        data = {
            'id': id,
            'offset': 0,
            'total': True,
            'limit': 5000,
            'n': 5000,
            'csrf_token': self.csrf
        }
        # print(data)
        ret = self.session.post(target_url, data=encrypted_request(data), headers=self.headers)
        # print(ret)
        return json.loads(ret.text)['playlist']['tracks']

    def get_br_by_privilege(self, all_quality):
        '''根据原先设置的优先级确定某一首歌曲的码率
        '''
        selected_quality = -1
        for current_br in range(0, len(self.privilege)):
            if all_quality[self.privilege[current_br]]:
                selected_quality = self.privilege[current_br]
                break
        return selected_quality

    def parse_playlist_detail(self, raw_playlist_detail):
        '''对从网易云获取到的信息进行整合

        Args:
            raw_playlist_detail<list>:刚刚从网易云中获取到的信息
        Ret:
            <list>:整理过的信息
        '''
        ret_info = []

        # 将被选为同一个码率的歌曲“包装”在一起，我实在是想不到什么好的取名方式了
        pack = {}

        file_name = {}
        for single_song_detail in raw_playlist_detail:
            temp = {}
            temp['song_name'] = single_song_detail['name']
            temp['album'] = {}
            temp['artists'] = []

            combined_artists = ''
            for artist in single_song_detail['ar']:
                temp['artists'].append(artist['name'])
                combined_artists = combined_artists + artist['name'] + ','

            file_name[single_song_detail['id']] = combined_artists[:-1] + ' - ' + single_song_detail['name']
            # 可能有album的key就一定会有值？
            if 'al' in single_song_detail and single_song_detail['al']:
                temp['album']['picUrl'] = single_song_detail['al']['picUrl']
                temp['album']['name'] = single_song_detail['al']['name']
            quality = {}

            quality['h'] = single_song_detail['h']['br'] if single_song_detail['h'] else None  # high
            quality['m'] = single_song_detail['m']['br'] if single_song_detail['m'] else None  # middle
            quality['l'] = single_song_detail['l']['br'] if single_song_detail['l'] else None  # low
            quality_id = single_song_detail[self.get_br_by_privilege(quality)]['br']
            if quality_id in pack:
                pack[quality_id].append(single_song_detail['id'])
            else:
                pack[quality_id] = [single_song_detail['id']]

            ret_info.append(temp)
        return ret_info, pack, file_name

    '''以下的全是旧版本的api'''

    def get_playlist_detail(self, playlist_url=None, playlist_id=None):
        '''获取歌单的信息

        Args:
            playlist_url<str>:歌单网站
            playlist_id<str/int>:歌单id
            二选一即可
        Ret:
            json<dict>:歌单信息
        '''
        id = None
        if not playlist_url and not id:
            raise ValueError('Need url or id')
        elif playlist_url and playlist_id:
            id = playlist_id
        elif playlist_id:
            id = playlist_id
        else:
            id = playlist_url.split('playlist?id=')[1]
        target_url = 'http://music.163.com/api/playlist/detail?id={}'.format(id)
        ret = None
        try:
            ret = json.loads(self.session.get(target_url).text)
        except requests.exceptions.RequestException as e:
            print(e)
            ret = {}
        return ret

    def get_song_detail(self, id):
        '''获取单曲的信息

        Args:
            id<str/int>:单曲的id
        Ret:
            json:单曲信息
        '''
        target_url = 'http://music.163.com/api/song/detail/?id={}&ids=[{}]'.format(id, id)
        ret = None
        try:
            ret = json.loads(self.session.get(target_url).text)
            # print(ret)
        except requests.exceptions.RequestException as e:
            print(e)
            ret = {}
        return ret

    def encrypted_id(self, id):
        '''歌曲加密算法, 基于https://github.com/yanunon/NeteaseCloudMusic脚本实现'''
        magic = bytearray('3go8&$8*3*3h0k(2)2', 'u8')
        song_id = bytearray(id, 'u8')
        magic_len = len(magic)
        for i, sid in enumerate(song_id):
            song_id[i] = sid ^ magic[i % magic_len]
        m = hashlib.md5(song_id)
        result = m.digest()
        result = base64.b64encode(result)
        result = result.replace(b'/', b'_')
        result = result.replace(b'+', b'-')
        return result.decode('utf-8')

    def download_single_song(self, file_folder, song_info, privilege=None):
        '''下载单首歌
        Error: Unfinished

        Error: id有问题，应该是dfsid,但返回的dfsid全是0了

        Args:
            file_folder<str>:要下载到的文件夹
            song_info<dict>:用get_song_info函数获取到的dict
            privilege<list>:下载品质的优先级
                可选内容为mp3Url，bMusic，lMusic，mMusic，hMusic，都为str
        '''
        if not privilege:
            privilege = ['mMusic', 'lMusic', 'hMusic', 'mp3Url']
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        combined_artists = ''
        for artist in song_info['artists']:
            combined_artists = combined_artists + artist + ','
        file_path = os.path.join(file_folder, combined_artists[:-1] + ' - ' + song_info['name'] + '.mp3')
        print(file_path)
        # 优先级
        selected_privilege = None
        for selected_privilege_temp in privilege:
            if selected_privilege_temp in song_info['quality_id']:
                selected_privilege = selected_privilege_temp
                break
        print(selected_privilege)
        enc_id = self.encrypted_id(song_info['quality_id'][selected_privilege])
        if not os.path.exists(file_path):
            target_url = 'http://m%s.music.126.net/%s/%s.mp3' % (
                random.randrange(1, 3), enc_id, song_info['quality_id'][selected_privilege])
            print(target_url)
        pass

    def get_song_info(self, raw_info):
        '''对网易云获取到的歌曲信息进行整理
           一是为了下载，二是为了写入到mp3文件中

        Args:
            raw_info<dict>:刚刚从网易云中获取到的信息
        Ret:
            dict<dict>:整理过的信息

        TODO:
            怎么获取流派，网易云返回的'album'下的'type'是什么
        '''
        raw_info = raw_info['songs'][0]
        ret_info = {}
        # 歌曲名
        ret_info['name'] = raw_info['name']

        # 歌手名
        # 可能会有多个歌手
        ret_info['artists'] = []
        for one_artist in raw_info['artists']:
            ret_info['artists'].append(one_artist['name'])
        if raw_info['album']:
            ret_info['album'] = raw_info['album']['name']
            # 专辑发布时间
            ret_info['publishTime'] = datetime.datetime.utcfromtimestamp(
                int(raw_info['album']['publishTime']) / 1000) + datetime.timedelta(hours=8)

        # 专辑图片
        ret_info['pic_url'] = raw_info['album']['picUrl']

        # media quality
        ret_info['quality_id'] = {}
        if raw_info['hMusic']:
            ret_info['quality_id']['hMusic'] = str(raw_info['hMusic']['id'])
        if raw_info['mMusic']:
            ret_info['quality_id']['mMusic'] = str(raw_info['mMusic']['id'])
        if raw_info['lMusic']:
            ret_info['quality_id']['lMusic'] = str(raw_info['lMusic']['id'])
        if raw_info['mp3Url']:
            ret_info['quality_id']['mp3Url'] = str(raw_info['mp3Url'])

        return ret_info
