# encoding=utf-8
# python3
import getopt
import os
import sys

from . import download_main
from . import tools
from .gui import MainWindow
from . import configuration


def main():
    configuration.config = configuration.Config(os.path.join(os.getcwd(), 'config'))
    if len(sys.argv) == 1:
        # Start gui
        print('Starting gui inferface')
        window = MainWindow()
        window.place_widget()
        window.mainloop()
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "m:p:w:e:", ['music=', 'pic=', 'wait=', 'extra='])
        except getopt.GetoptError:
            # print help information and exit:
            print('Error: GetoptError')
            return
        music_folder = None
        pic_folder = None
        wait_time = 0
        extra_music_file = None
        for o, a in opts:
            if o in ('-m', '--music'):
                music_folder = a
            if o in ('-p', '--pic'):
                pic_folder = a
            if o in ('-w', 'wait'):
                wait_time = a
            if o in ('-e', '--extra'):
                extra_music_file = a
        if not music_folder or not os.path.exists(music_folder):
            music_folder = configuration.config.get_config('music_folder')
            print('Error occured! Set music_folder to default: %s' % music_folder)
        if not pic_folder or not os.path.exists(pic_folder):
            pic_folder = configuration.config.get_config('pic_folder')
            print('Error occured! Set pic_folder to default: %s' % pic_folder)
        download_main.ne.set_wait_interval(wait_time)
        for arg in args:
            error_songs_list = download_main.download_netease_playist(str(arg), music_folder, pic_folder)
            download_main.download_songs_via_searching(error_songs_list, music_folder, pic_folder, extra_music_file)


if __name__ == '__main__':
    main()
