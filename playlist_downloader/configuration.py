# encoding=utf-8
# python3
import os
import json

from . import tools


class Config(object):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        USER_FOLDER = os.path.expanduser("~")
        if not os.path.exists(self.config_file_path):

            # Default config
            self.config = {
                'music_folder': os.path.join(USER_FOLDER, 'music_save'),
                'pic_folder': os.path.join(USER_FOLDER, 'pic_save'),
                'extra_music_file': os.path.join(USER_FOLDER, 'extra_music_file.txt'),
                'wait_time': 0.5
            }
        else:
            with open(self.config_file_path, 'r', encoding='utf-8') as config_file:
                self.config = json.loads(config_file.read())
                if not 'music_folder' in self.config:
                    self.config['music_folder'] = os.path.join(USER_FOLDER, 'music_save')
                if not 'pic_folder' in self.config:
                    self.config['pic_folder'] = os.path.join(USER_FOLDER, 'pic_save')
                if not 'extra_music_file' in self.config:
                    self.config['extra_music_file'] = os.path.join(USER_FOLDER, 'extra_music_file.txt')
                if not 'wait_time' in self.config:
                    self.config['wait_time'] = 0.5

    def get_config(self, key):
        '''
            key 应为以下几个:
                music_folder
                pic_folder
                extra_music_file
                wait_time
        '''
        if key in self.config:
            return self.config[key]

    def set_config(self, v, key=None):
        if not key:
            self.config = v
        else:
            self.config[key] = v

    def save_config(self):
        with open(self.config_file_path, 'w+', encoding='utf-8') as config_file:
            tools.logger.log('Save config', level=tools.logger.DEBUG)
            config_file.write(str(json.dumps(self.config)))


config = Config(os.path.join(os.getcwd(), 'config'))
