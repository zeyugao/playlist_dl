## Introduction

Download playlist from netease

根据网易云的用户/公共歌单来下载歌曲到电脑

并从网易云上更新封面，专辑名，专辑发布时间，标题，歌手到mp3

## Usage


> py -m  playlist_downloader playlist_urls/playlist_ids

可以同时添加多条playlist的信息

eg:

> py -m  playlist_downloader http://music.163.com/#/playlist?id=907018095

Or

> py -m  playlist_downloader 907018095

可以一次进行多个playlist的下载

eg:

> py -m  playlist_downloader http://music.163.com/#/playlist?id=907018095 http://music.163.com/#/playlist?id=123656572

Or

> py -m  playlist_downloader 907018095 123656572 58084349

 -  extra_music_file.txt的说明

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

## 命令行版本

> -m 或者 --music

指定保存音乐文件的文件夹

> -p 或者 --pic

指定保存专辑封面的文件夹

> -w 或者 wait

下载两个mp3之间的时间间隔

> -e 或者 --extra

指定保存额外的需要下载的歌曲的信息的文件，格式同extra_music_file.txt

## Gui版本

 - Input playlist url or playlist id的Text控件：

 添加playlist的信息，每行一条，可以是url，也可以是id

---

 - Music folder:

 保存音乐文件的文件夹，点击Change按钮可以以对话框的形式选择文件夹

---

 - Album picture folder:

 保存专辑的封面的文件夹，点击Change按钮可以以对话框的形式选择文件夹

---

 - Extra music file:

 额外的需要下载的歌曲的信息，格式同extra_music_file.txt

 点击Edit可以打开一个新窗口编辑选择的文件

 点击Change按钮可以以对话框的形式选择文件

---
 - Start downloading按钮:

开始下载

---

**下载时，还不能中途暂停、取消**

进度条显示的是当前下载的音乐文件的进度，

## 保存

网易云的歌曲会在文件下生成以用户的昵称以及歌单的id的文件夹

用搜索方式的会保存在extra_music下

目录结构(eg)：
```
music_save
├─User_1
│  ├─907018095
│  │  ├─Taylor Swift - Love Story.mp3
│  │  └─Taylor Swift - Innocent.mp3
|  └─123656572
│     └─Taylor Swift - Back To December.mp3
├─User_2
│  ├─901248095
│  │  └─Taylor Swift - Love Story.mp3
│  └─165475572
│     └─Taylor Swift - Back To December.mp3
└─extra_music
   └─Ed Sheeran - Perfect.mp3
```


## 要求/Requirements

```
Python3
requests
pycryptodome
mutagen
```
lastest version is enough
## TOOD
- [ ] 完成music-api-jwzcyzizya.now.sh的搜索
- [ ] 可选的码率（在args中进行选择）

## 致谢

[网易云下载 by 糖果君](https://greasyfork.org/scripts/23222-%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD/code/%E7%BD%91%E6%98%93%E4%BA%91%E4%B8%8B%E8%BD%BD.user.js)

[musicbox](https://github.com/darknessomi/musicbox)