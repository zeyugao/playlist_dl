---
layout: page
title: Usage
---

项目的地址在这：[playlist_dl](https://github.com/Zeyugao/playlist_dl)

~~如果你的系统是Windows Vista及以上，可以直接下载打包好的程序文件，~~由于pyinstaller对Crypto的支持问题，暂时不打包

# Preparation

0、下面的网站都有可能被墙

1、下载[set_up_env_script.bat]({{site.baseurl}}/upload/set_up_env_script.bat)

2、下载[aria2-1.34.0-win-32bit-build1.zip](https://github.com/aria2/aria2/releases/download/release-1.34.0/aria2-1.34.0-win-32bit-build1.zip)，解压后的目录结构应该是这样的

```
└─aria2-1.34.0-win-64bit-build1
       aria2c.exe
       AUTHORS
       ChangeLog
       COPYING
       LICENSE.OpenSSL
       NEWS
       README.html
       README.mingw
```

3、把set_up_env_script.bat和aria2c.exe放在一起，目录结构应该变为
```
└─aria2-1.34.0-win-64bit-build1
       aria2c.exe
       set_up_env_script.bat
       AUTHORS
       ChangeLog
       COPYING
       LICENSE.OpenSSL
       NEWS
       README.html
       README.mingw
```

4、运行set_up_env_script.bat，等它显示Installing finished

5、下载这个文件[master.zip](https://github.com/Zeyugao/playlist_dl/archive/master.zip)
直接解压后的文件结构应该是
```
└─playlist_dl-master
   └─playlist_dl-master
      │  .gitignore
      │  LICENSE
      │  README.md
      └─playlist_dl
            download_main.py
            extra_music_file.txt
            gui.py
            main.py
            netease.py
            search.py
            tools.py
            __init__.py
            __main__.py
```

6、下载这个文件[run_program.bat]({{site.baseurl}}/upload/run_program.bat)，把它放到刚才下载的playlist_dl-master的文件夹下面，使其与playlist_dl文件夹同级，预期的文件结构应该变为
```
└─playlist_dl-master
   └─playlist_dl-master
      │  .gitignore
      │  LICENSE
      │  README.md
      |  run_program.bat
      └─playlist_dl
            download_main.py
            extra_music_file.txt
            gui.py
            main.py
            netease.py
            search.py
            tools.py
            __init__.py
            __main__.py
```

# Run

运行run_program.bat就可以了

# 使用说明

参见[使用说明](https://github.com/Zeyugao/playlist_dl#%E5%91%BD%E4%BB%A4%E8%A1%8C%E7%89%88%E6%9C%AC)

保存的文件格式，参见[保存](https://github.com/Zeyugao/playlist_dl#%E4%BF%9D%E5%AD%98)

把你的歌单的网址填到“Input playlists url or ids”的下面的那个文本框里面（一行代表一个网址或一个id）

例如网址是http://music.163.com/#/playlist?id=**2277861412**，则这个歌单对应的id就是2277861412，直接把网址粘贴过去就可以了，会识别的

点了Start downloading后，运行的时候长大概这样![screenshot_1]({{site.baseurl}}/upload/screenshot_1.png)

理论上，只要你能把歌曲添加到歌单里面，就可以easily下载下来，对于那些需要一些版权下载，但是可以保存到歌单的音乐也有效。

而对于那些，因为版权原因或者要付费（在App里面应该会说明）而既不能听，也不能保存到歌单的歌曲，可以把它写进extra music file里面，让程序在qq音乐里面搜索。

最好是在其他的音乐网站上查找一下在网易云上无法保存或者缺失的歌曲，提供精确的歌曲名、歌手名、专辑名，以及根据[Usage](https://github.com/Zeyugao/playlist_dl#usage)里面的“extra_music_file.txt的说明”，填入你自己定义的文件中，让程序去读取

为了避免编码的问题，不要直接新建文件，用默认的文件位置，点个Edit，让程序去新建。以后要改，直接用程序去修改。