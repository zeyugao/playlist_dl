# encoding=utf-8
# python3
import getopt
import os
import sys

from . import download_func
from . import tools
from .gui import MainWindow
from . import configuration


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:p:w:e:m:", ['music=', 'pic=', 'wait=', 'extra=', 'mode='])
    except getopt.GetoptError:
        # print help information and exit:
        tools.logger.log('Error: GetoptError', tools.logger.ERROR)
        return
    for o, a in opts:
        if o in ('-m', '--music'):
            music_folder = a
            configuration.config.set_config(music_folder, key='music_folder')
        if o in ('-p', '--pic'):
            pic_folder = a
            configuration.config.set_config(pic_folder, key='pic_folder')
        if o in ('-w', 'wait'):
            wait_time = a
            configuration.config.set_config(wait_time, key='wait_time')
        if o in ('-e', '--extra'):
            extra_music_file = a
            configuration.config.set_config(extra_music_file, key='extra_music_file')
        if o in ('-m', '--mode'):
            if a in ('DEBUG', 'INFO', 'WARNING', 'ERROR'):
                tools.logger.set_level(a)
            else:
                tools.logger.log('Invaid mode: %s' % a, level=tools.logger.WARNING)
    if args == []:
        # Start gui
        tools.logger.log('Starting gui inferface', tools.logger.INFO)
        window = MainWindow()
        window.place_widget()
        window.mainloop()
    else:
        if tools.logger.level > tools.logger.INFO:
            tools.logger.set_level(tools.logger.INFO)
        configuration.config.save_config()
        download_func.ne.set_wait_interval(configuration.config.get_config('wait_time'))
        tools.logger.log('Set wait time: %d' % (configuration.config.get_config('wait_time')), level=tools.logger.DEBUG)
        music_folder = configuration.config.get_config('music_folder')
        pic_folder = configuration.config.get_config('pic_folder')
        extra_music_file = configuration.config.get_config('extra_music_file')
        for arg in args:
            error_songs_list = download_func.download_netease_playist(str(arg), music_folder, pic_folder)
            download_func.download_songs_via_searching(error_songs_list, music_folder, pic_folder, extra_music_file)


if __name__ == '__main__':
    main()
