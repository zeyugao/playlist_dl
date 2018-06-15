# encoding=utf-8
# python3
import getopt
import os
import sys

import download_main
import tools
from gui import MainWindow


def main():
    if len(sys.argv) == 1:
        # Start gui
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
            if o in ('-e','--extra'):
                extra_music_file = a
        if not music_folder or not os.path.exists(music_folder):
            music_folder = os.path.join(tools.USER_FOLDER, 'music_save')
            print('Error occured! Set music_folder to default: %s' % music_folder)
        if not pic_folder or not os.path.exists(pic_folder):
            pic_folder = os.path.join(tools.USER_FOLDER, 'pic_save')
            print('Error occured! Set pic_folder to default: %s' % pic_folder)
        download_main.ne.set_wait_interval(wait_time)
        for arg in args:
            download_main.download_playist(str(arg), music_folder, pic_folder, extra_music_file)


if __name__ == '__main__':
    main()
