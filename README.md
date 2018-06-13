## Introduction

Download playlist from netease

根据网易云的用户/公共歌单来下载歌曲到电脑

并从网易云上更新封面，专辑名，专辑发布时间，标题，歌手到mp3

## Usage


> py main.py playlist_url/playlist_id

eg:

> py main.py http://music.163.com/#/playlist?id=907018095

Or

> py main.py 907018095

### extra_music_file.txt

加入无法在网易云上收藏到歌单中的音乐

每一行包括一首歌，歌曲的信息依次为“歌曲名”、“作者”、“专辑名”、“目标音乐网站的代号”，之间用分号隔开（;)（英文分号）

音乐网站|代码
---|---
网易云|netease
QQ|qq
酷狗|kugou
酷我|kuwo
虾米|xiami
百度|baidu
一听|1ting
咪咕|migu
荔枝|lizhi
蜻蜓|qingting
喜马拉雅|ximalaya
全民K歌|kg
5sing原创|5singyc
5sing翻唱|5singfc

eg:

> Liability;Lorde;Melodrama;qq

如果不知道作者或者专辑名，或者没有对其的需求，则可以空着，但必须加入分号（;）

eg:

> Liability;Lorde;;qq

必须添加音乐网站的代码


### TOOD
- [ ] 完成music-api-jwzcyzizya.now.sh的搜索
- [ ] 可选的码率（在args中进行选择）

## 致谢

[网易云下载 by 糖果君](https://greasyfork.org/scripts/23222-%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD/code/%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD.user.js)

[musicbox](https://github.com/darknessomi/musicbox)