# encoding=utf-8
# python3

import requests
import json
import hashlib
import base64
import os
import binascii
from Crypto.Cipher import AES
from http.cookiejar import LWPCookieJar


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


def encrypted_id(id):
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


class NetEase(object):
    '''包装网易云的api'''

    def __init__(self):
        self.headers = {
            # 'Cookie': 'appver=1.5.2',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36')
        }
        self.session = requests.Session()
        self.set_privilege_weapi()
        self.set_save_folder()
        self.csrf = ''

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

    def set_privilege_weapi(self, privilege_br=None):
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
            print('File: %s already exists, skip' % file_path)
            return
        if os.path.exists(file_path):
            os.remove(file_path)

        respond = self.session.get(url, stream=True)
        file_lenght = int(respond.headers.get('content-length'))
        print('File size: %s B, %s KB' % (int(file_lenght), int(file_lenght / 1024)), end='')
        with open(file_path, 'wb') as file:
            for chunk in respond.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print('-Done')

    def download_album_pic_and_save(self, url, file_name, overwrite=False):
        pic_path = os.path.join(self.pic_folder, file_name + '.jpg')
        print('Download album pic: %s.jpg' % file_name)
        self.download_file(url, pic_path)
        return pic_path

    def download_single_song_and_save(self, url, file_name, overwrite=False):
        file_path = os.path.join(self.music_folder, file_name + '.mp3')
        print('Download song: %s.mp3' % file_name)
        self.download_file(url, file_path)
        return file_path

    def search_song(self, song_id, song_name):
        ret_url = self.search_song_netease(song_id)
        return ret_url if ret_url else self.search_song_xiami(song_name)
        pass

    # 下面两个函数参考https://greasyfork.org/scripts/23222-%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD/code/%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD.user.js
    def search_song_xiami(self, song_name):
        '''网易云不允许下载时用虾米的接口

        Args:
            song_name<str>:歌曲名+歌手名组合成的字符串
        Ret:
            <str>:下载url
        '''
        print("Even couldn't find %s on NetEase, now search on xiami" % song_name)
        target_url = 'http://musicafe.co:8080/api/search/song/xiami?&limit=1&page=1&key=' + song_name
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Host': 'musicafe.co',
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36')
        }
        ret = json.loads(requests.get(target_url, headers=headers).text)
        if ret['success']:
            return ret['songList'][0]['file']
        else:
            print('Faild search on xiami')
            return

    def search_song_netease(self, song_id):
        '''在无法直接获得歌曲的url时候用搜索的方式来获得歌曲下载地址

        Args:
            song_id<str/int>:在网易云音乐上的歌曲id
            song_name<str>:歌曲名+歌手名组合成的字符串
            Ret:
                <str>:下载url
        '''
        # target_url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token=' + self.csrf

        print("Couldn't download directly, now search on NetEase")
        target_url = 'http://music.163.com/weapi/search/pc'
        data = {
            's': str(song_id),
            'limit': 1,
            'type': 1,
            'offset': 0,
        }
        ret = None
        try:
            ret = json.loads(self.session.post(target_url, data=encrypted_request(
                data), headers=self.headers).text)['result']['songs'][0]
        except IndexError:
            print('Can not get song')
            return
        # TODO:提供品质的选择
        quality_privilege = {1: 'mMusic', 0: 'hMusic', 2: 'lMusic', 3: 'bMusic'}
        music = {}
        for i in range(0, len(quality_privilege)):
            if ret[quality_privilege[i]]:
                music = ret[quality_privilege[i]]
                break
        dfsId = None
        if 'dfsId' in music:
            dfsId = music['dfsId']
        if 'dfsId_str' in music:
            dfsId = music['dfsId_str']
        target_url = None
        if music and dfsId:
            target_url = 'http://p2.music.126.net/%s/%s.jpg.mp3' % (encrypted_id(str(dfsId)), dfsId)
        elif not ret['mp3Url'].endswith('==/0.mp3'):
            target_url = ret['mp3Url']
        return target_url

    def get_songs_info_weapi(self, songs_id, quality):
        target_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token=' + self.csrf

        data = {
            'ids': songs_id,
            'br': quality,
            'csrf_token': self.csrf
        }
        ret = self.session.post(target_url, data=encrypted_request(data), headers=self.headers)

        json_temp = json.loads(ret.text)
        if json_temp['code'] == 200:
            return json_temp['data']
        else:
            print('Error! Code: %s' % json_temp['code'])
            return []

    def get_and_parse_playlist_detail_weapi(self, playlist_url):
        '''
        Args:
            playlist_url:歌单网站
            playlist_id:歌单id
            二选一即可
        Ret:
            ret_info<dict>:
                并以歌曲id作为关键字
                包含
                    song_name:歌曲名
                    album<name,picUrl>:专辑的名字，专辑封面
                    artists:参与创作的艺术家
                    file_name:当前歌曲应该保存的文件名
            pack<dict>:相同码率的进行包装
        '''

        return self.parse_playlist_detail_weapi(self.get_playlist_detail_weapi(playlist_url))

    def get_playlist_detail_weapi(self, playlist_url):
        '''用新版的weapi获取歌单信息
        Args:
            playlist_url:歌单网站
            playlist_id:歌单id
            二选一即可
        Ret:
            json:歌单信息

        '''
        # print('get_playlist_detail_weapi func begin')
        try:
            id_ = playlist_url.split('playlist?id=')[1]
        except IndexError as e:
            print('Please input correct url')
            return
        target_url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token=' + self.csrf
        data = {
            'id': id_,
            'offset': 0,
            'total': True,
            'limit': 5000,
            'n': 5000,
            'csrf_token': self.csrf
        }
        json_temp = json.loads(self.session.post(target_url, data=encrypted_request(data), headers=self.headers).text)
        if json_temp['code'] == 200:
            return json_temp['playlist']['tracks']
        else:
            print('Error! Code: %s', json_temp['code'])
            return json_temp['data']

    def get_quality_by_privilege_weapi(self, all_quality):
        '''根据原先设置的优先级确定某一首歌曲的码率
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

    def parse_playlist_detail_weapi(self, raw_playlist_detail):
        '''对从网易云获取到的信息进行整合

        Args:
            raw_playlist_detail<list>:刚刚从网易云中获取到的信息
        Ret:
            info_ret<dict>:
                并以歌曲id作为关键字
                包含
                    title:歌曲名
                    album<name,picUrl>:专辑的名字，专辑封面
                    artists:参与创作的艺术家
                    file_name:当前歌曲应该保存的文件名
            pack<dict>:相同码率的进行包装
        '''
        if raw_playlist_detail is None:
            return {}, {}
        info_ret = {}

        # 将被选为同一个码率的歌曲“包装”在一起，我实在是想不到什么好的取名方式了
        pack = {}

        for single_song_detail in raw_playlist_detail:
            temp = {}
            temp['title'] = single_song_detail['name']
            temp['album'] = {}
            temp['artists'] = ''

            for artist in single_song_detail['ar']:
                temp['artists'] = temp['artists'] + artist['name'] + ','
            temp['artists'] = temp['artists'][:-1]

            if len(temp['artists']) > 60:
                # 如果艺术家过多导致文件名过长，则文件名的作者则为第一个艺术家的名字
                print('Song: %s\'s name too long, cut' % single_song_detail['name'])
                temp['file_name'] = temp['artists'].split(',')[0] + ' - ' + single_song_detail['name']
            else:
                temp['file_name'] = temp['artists'] + ' - ' + single_song_detail['name']
            temp['artists'] = temp['artists'].replace(',', ';')
            temp['file_name'] = self.replace_file_name(temp['file_name'])

            temp['id'] = single_song_detail['id']

            # 可能有album的key就一定会有值？
            if 'al' in single_song_detail and single_song_detail['al']:
                temp['album']['picUrl'] = single_song_detail['al']['picUrl']
                temp['album']['name'] = single_song_detail['al']['name']
            quality = {}

            quality['h'] = single_song_detail['h']['br'] if single_song_detail['h'] else None  # high
            quality['m'] = single_song_detail['m']['br'] if single_song_detail['m'] else None  # middle
            quality['l'] = single_song_detail['l']['br'] if single_song_detail['l'] else None  # low
            quality_id = single_song_detail[self.get_quality_by_privilege_weapi(quality)]['br']
            if quality_id in pack:
                pack[quality_id].append(single_song_detail['id'])
            else:
                pack[quality_id] = [single_song_detail['id']]

            info_ret[single_song_detail['id']] = temp
        return info_ret, pack
