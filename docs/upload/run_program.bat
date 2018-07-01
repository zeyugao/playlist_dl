@echo off

ver|findstr "[3-5]\.[0-9]\.[0-9][0-9]*" > nul && (goto isBelowNT6)

C:\Python36\python.exe -m playlist_downloader

:isBelowNT6

C:\Python34\python.exe -m playlist_downloader