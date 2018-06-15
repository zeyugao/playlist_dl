# encoding=utf-8
# python3
from gui import MainWindow
from download_main import download_playist
import sys
import os
import tools


def main():
    if len(sys.argv) == 1:
        # Start gui
        window = MainWindow()
        window.place_widget()
        window.mainloop()
    else:
        default_music_folder = os.path.join(tools.USER_FOLDER, 'music_save')
        default_pic_folder = os.path.join(tools.USER_FOLDER, 'pic_save')
        download_playist(str(sys.argv[1]), default_music_folder, default_pic_folder)


if __name__ == '__main__':
    main()
