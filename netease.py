# encoding=utf-8
# python3

import base64
import binascii
import hashlib
import json
import os
import time

import eyed3
import requests

from Crypto.Cipher import AES

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


fake_headers = {
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


def wait(wait_time=1):
    print('Wait for %ds' % wait_time)
    time.sleep(wait_time)  # 防止被网易ban


session = requests.Session()
csrf = ''


def download_playist(playlist_url,
                     music_folder='./music_save/',
                     pic_folder='./pic_save/',
                     privilege={1: 'h', 0: 'm', 2: 'l'}):
    '''
        Args:
            privilege_br<dict>:
                eg:
                    privilege_br = {
                        0: 'h',  # high quality, fisrt
                        1: 'm',  # middle quality, second
                        2: 'l'   # low quality, third
                        }
            默认的码率:依次为m,h,l

    '''
    # check music folder
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)

    # song_info_sortby_id, playlist_detail_sortby_br = get_and_parse_playlist_detail_weapi(playlist_url)
    raw_playlist_detail = get_playlist_detail_weapi(playlist_url)
    print(raw_playlist_detail)
    # song_info_sortby_id:以歌曲的id作为关键字，用于添加mp3信息
    # playlist_detail_sortby_br:以歌曲的码率作为关键字，用于提交到网易云批量下载mp3
    song_info_sortby_id, playlist_detail_sortby_br = parse_playlist_detail_weapi(raw_playlist_detail, privilege)
    print(song_info_sortby_id)
    print(playlist_detail_sortby_br)
    for (br, ids) in playlist_detail_sortby_br.items():
        all_songs_info = get_songs_info_weapi(ids, br)
        print(all_songs_info)
        for single_song_info in all_songs_info:
            current_song_info = song_info_sortby_id[single_song_info['id']]

            if single_song_info['url']:
                download_and_modify_song(single_song_info['url'], current_song_info)
            else:
                # 当无法获取到歌曲的下载链接的时候
                get_song_info_by_album_method()


'''
            song_download_url = None
            if single_song_info['url']:
                song_download_url = single_song_info['url']
            else:
                song_download_url = search_song(single_song_info['id'], current_song_info['file_name'])
            if song_download_url is None:
                print('Faild download song %s' % current_song_info['file_name'])
                continue
            file_path = download_single_song_and_save(
                song_download_url, music_folder, current_song_info['file_name'], md5=single_song_info['md5'])
            pic_path = download_album_pic_and_save(current_song_info['album']['picUrl'], pic_folder,
                                                   current_song_info['file_name'])
            current_song_info['pic_path'] = pic_path
            print('Modify info for song: %s' % current_song_info['file_name'])
            modify_info(file_path, current_song_info)
'''


def get_song_info_by_album_method(album_id, song_id):
    pass


def get_song_info_by_xiami_api(song_name, song_artist):
    pass


def download_and_modify_song(song_download_url, single_song_full_info):
    pass


def modify_info(mp3_path, custom_info):
    '''修改mp3文件的信息
    Args:
        mp3_path<str>:mp3文件的路径
        kwargs<dict>:
            title:标题
            artists:作者
            album:所属专辑
            pic_path:专辑封面的路径
    '''
    audiofile = eyed3.load(mp3_path)
    audiofile.initTag()
    if 'artists' in custom_info:
        audiofile.tag.artist = custom_info['artists']  # .decode('utf-8')
    if 'title' in custom_info:
        audiofile.tag.title = custom_info['title']  # .decode('utf-8')

    if 'album' in custom_info:
        audiofile.tag.album = custom_info['album']['name']  # .decode('utf-8')

    if 'pic_path' in custom_info:
        # No check here
        # TODO
        with open(custom_info['pic_path'], 'rb') as pic_file:
            imagedata = pic_file.read()
            audiofile.tag.images.set(3, imagedata, 'image/jpeg', u'')
    if 'time' in custom_info:
        audiofile.tag.recording_date = custom_info['time']
    if 'company' in custom_info:
        audiofile.tag.publisher = custom_info['company']
    audiofile.tag.save()


def download_file(url, file_path, overwrite=False):
    if os.path.exists(file_path) and not overwrite:
        print('File: %s already exists, skip' % file_path)
        return
    if os.path.exists(file_path):
        os.remove(file_path)
    respond = session.get(url, stream=True)
    file_lenght = int(respond.headers.get('content-length'))
    print('File size: %s B, %s KB' % (int(file_lenght), int(file_lenght / 1024)), end='')
    with open(file_path, 'wb') as file:
        for chunk in respond.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print('-Done')


def download_album_pic_and_save(url, pic_folder, file_name, overwrite=False):
    pic_path = os.path.join(pic_folder, file_name + '.jpg')
    print('Download album pic: %s.jpg' % file_name)
    download_file(url, pic_path)
    return pic_path


def download_single_song_and_save(url, music_folder, file_name, overwrite=False, md5=None):
    print(md5)
    file_path = os.path.join(music_folder, file_name + '.mp3')
    print('Download song: %s.mp3' % file_name)
    download_file(url, file_path)
    return file_path


def search_song(song_id, song_name):
    ret_url = search_song_netease(song_id)
    return ret_url if ret_url else search_song_xiami(song_name)


# 下面两个函数参考https://greasyfork.org/scripts/23222-%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD/code/%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD.user.js


def search_song_xiami(song_name):
    '''网易云不允许下载时用虾米的接口
    Args:
        song_name<str>:歌曲名+歌手名组合成的字符串
    Ret:
        <str>:下载url
    '''
    print("Even couldn't find %s on NetEase, now search on xiami" % song_name)
    target_url = 'http://music-api-jwzcyzizya.now.sh/api/search/song/xiami?&limit=1&page=1&key=' + song_name
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


def search_song_netease(song_id):
    '''在无法直接获得歌曲的url时候用搜索的方式来获得歌曲下载地址
    Args:
            song_id<str/int>:在网易云音乐上的歌曲id
            song_name<str>:歌曲名+歌手名组合成的字符串
            Ret:
                <str>:下载url
    '''
    # target_url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token=' + csrf
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
        ret = json.loads(session.post(target_url, data=encrypted_request(
            data), headers=fake_headers).text)['result']['songs'][0]
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


def get_songs_info_weapi(songs_id, quality):
    target_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token=' + csrf
    data = {
        'ids': songs_id,
        'br': quality,
        'csrf_token': csrf
    }
    ret = session.post(target_url, data=encrypted_request(data), headers=fake_headers)
    json_temp = json.loads(ret.text)
    if json_temp['code'] == 200:
        return json_temp['data']
    else:
        print('Error! Code: %s' % json_temp['code'])
        return []


"""
def get_and_parse_playlist_detail_weapi(playlist_url):
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
    return parse_playlist_detail_weapi(get_playlist_detail_weapi(playlist_url))
"""


def get_playlist_detail_weapi(playlist_url):
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
    except IndexError:
        print('Please input correct url')
        return
    target_url = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token=' + csrf
    data = {
        'id': id_,
        'offset': 0,
        'total': True,
        'limit': 5000,
        'n': 5000,
        'csrf_token': csrf
    }
    json_temp = json.loads(session.post(target_url, data=encrypted_request(data), headers=fake_headers).text)
    if json_temp['code'] == 200:
        return json_temp['playlist']['tracks']
    else:
        print('Error! Code: %s', json_temp['code'])
        return json_temp['data']


def get_quality_by_privilege_weapi(all_quality, privilege):
    '''根据原先设置的优先级确定某一首歌曲的码率
    '''
    selected_quality = -1
    for current_br in range(0, len(privilege)):
        if all_quality[privilege[current_br]]:
            selected_quality = privilege[current_br]
            break
    return selected_quality


def replace_file_name(file_name):
    t = ["\\", "/", "*", "?", "<", ">", "|", '"']
    for i in t:
        file_name = file_name.replace(i, '')
    return file_name


def parse_playlist_detail_weapi(raw_playlist_detail, privilege):
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
        temp['file_name'] = replace_file_name(temp['file_name'])
        temp['id'] = single_song_detail['id']
        # 可能有album的key就一定会有值？
        if 'al' in single_song_detail and single_song_detail['al']:
            temp['album']['picUrl'] = single_song_detail['al']['picUrl']
            temp['album']['name'] = single_song_detail['al']['name']
        quality = {}
        quality['h'] = single_song_detail['h']['br'] if single_song_detail['h'] else None  # high
        quality['m'] = single_song_detail['m']['br'] if single_song_detail['m'] else None  # middle
        quality['l'] = single_song_detail['l']['br'] if single_song_detail['l'] else None  # low
        quality_id = single_song_detail[get_quality_by_privilege_weapi(quality, privilege)]['br']
        if quality_id in pack:
            pack[quality_id].append(single_song_detail['id'])
        else:
            pack[quality_id] = [single_song_detail['id']]
        info_ret[single_song_detail['id']] = temp
    return info_ret, pack
