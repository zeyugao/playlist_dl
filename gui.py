# encoding=utf-8
# python3

import os
import tkinter
import tkinter.scrolledtext
from tkinter import messagebox, ttk
from tkinter.filedialog import askdirectory, askopenfilename
from time import sleep
import threading

import tools
import download_main


class ProgressBarWindow(object):
    def __init__(self, parent_window):
        self.root = tkinter.Toplevel(parent_window)
        self.root.title('')
        self.root.config(width=600, height=70)
        self.root.resizable(0, 0)
        self.root.protocol("WM_DELETE_WINDOW", self.diable_close_window)

        self.progressbar = {}

    def set_label(self,text):
        self.label['text'] = text
    def step(self, step):
        self.progressbar.step(step)
        self.progressbar.update()

    def set(self, value):
        self.progressbar['value'] = value

    def destory(self):
        self.root.destroy()

    def place_widget(self):
        self.label = ttk.Label(self.root,text = 'Fetching playlist detail')
        self.label.place(x = 10,y = 10)


        self.progressbar = ttk.Progressbar(self.root, mode='determinate',length = 580)
        self.progressbar.place(x = 10,y = 40,height = 20)
        self.progressbar['value'] = 0
        self.progressbar['maximum'] = 100

    def diable_close_window(self):
        pass


class EditWindow(object):
    def __init__(self, parant_window, file_path):
        # self.root = tkinter.Tk()
        self.root = tkinter.Toplevel(parant_window)
        self.root.title('Edit')
        self.root.config(width=500, height=300)
        self.root.resizable(0, 0)
        # self.root.attributes("-topmost", 1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        try:
            self.file = open(file_path, 'a+', encoding='utf-8')
            self.file.seek(0, 0)
            self.content_display = self.file.read()
        except IOError:
            messagebox.showerror('Error', "Can't open file: %s" % file_path, parent=self.root)

    def place_widget(self):
        self.text_display_file = tkinter.Text(self.root, wrap='none', font=("", 12), width=58, height=10)
        self.text_display_file.grid(row=0, column=0, sticky='nsew', columnspan=3)

        scrollbar_text_v = ttk.Scrollbar(self.root, command=self.text_display_file.yview, orient=tkinter.VERTICAL)
        scrollbar_text_v.grid(row=0, column=3, sticky='nsew')
        scrollbar_text_h = ttk.Scrollbar(self.root, command=self.text_display_file.xview, orient=tkinter.HORIZONTAL)
        scrollbar_text_h.grid(row=1, column=0, sticky='nsew', columnspan=3)

        self.text_display_file['yscrollcommand'] = scrollbar_text_v.set
        self.text_display_file['xscrollcommand'] = scrollbar_text_h.set

        button_cancel = ttk.Button(self.root, text='Save and exit', command=self.save_and_exit)
        button_cancel.grid(row=2, column=2, sticky='w')

        button_save = ttk.Button(self.root, text='Cancel', command=self.destory)
        button_save.grid(row=2, column=2, sticky='e')

        self.text_display_file.insert(tkinter.END, self.content_display)

    def save_and_exit(self):
        self.save_file()
        self.destory()

    def save_file(self):
        new_content = self.text_display_file.get('1.0', tkinter.END)
        try:
            self.file.write(new_content)
        except IOError:
            messagebox.showerror('Error', "Can't write file", parent=self.root)

    def on_exit(self):
        result = messagebox.askyesnocancel('On exit', 'Do you want to save the file?', parent=self.root)
        if result:
            self.save_and_exit()
        elif result is None:
            return
        else:
            self.destory()

    def destory(self):
        self.file.close()
        self.root.destroy()


class MainWindow(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('netease playlist downloader')
        self.root.config(width=500, height=325)
        self.root.resizable(0, 0)
        self.music_folder = os.path.join(tools.USER_FOLDER, 'music_save')
        self.pic_folder = os.path.join(tools.USER_FOLDER, 'pic_save')
        self.extra_music_file = os.path.join(tools.USER_FOLDER, 'extra_music_file.txt')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())

    def ask_for_music_folder(self):
        path = askdirectory().replace('/', '\\')
        if os.path.exists(path):
            self.music_folder = path
            self.entry_music_folder['state'] = 'normal'
            self.music_folder_display.set(path)
            self.entry_music_folder['state'] = 'readonly'

    def ask_for_pic_folder(self):
        path = askdirectory().replace('/', '\\')
        if os.path.exists(path):
            self.pic_folder = path
            self.entry_pic_folder['state'] = 'normal'
            self.pic_folder_display.set(path)
            self.entry_pic_folder['state'] = 'readonly'

    def ask_for_extra_music_file(self):
        path = askopenfilename().replace('/', '\\')
        if os.path.exists(path):
            self.extra_music_file = path
            self.entry_extra_music_file['state'] = 'normal'
            self.extra_music_file_display.set(path)
            self.entry_extra_music_file['state'] = 'readonly'

    def edit_extra_music_file(self):
        if not os.path.exists(self.extra_music_file):
            result = messagebox.askyesno('Question', "File: %s doesn't exist.\ndo you want to create it?" % self.extra_music_file)
            if not result:
                return
        edit_window = EditWindow(self.root, self.extra_music_file)
        edit_window.place_widget()
        # edit_window.mainloop()

    def place_widget(self):

        label_input_playlist = ttk.Label(self.root,
                                         text='Input playlist url or playlist id:')
        label_input_playlist.place(x=20, y=20)

        # 用户输入url或者id的框
        self.text_input_playlist = tkinter.Text(self.root, height=7, wrap='none')
        self.text_input_playlist.place(x=20, y=50, width=440)

        scrollbar_text_input_v = ttk.Scrollbar(self.root, command=self.text_input_playlist.yview, orient=tkinter.VERTICAL)
        scrollbar_text_input_v.place(x=460, y=50, height=95)

        scrollbar_text_input_h = ttk.Scrollbar(self.root, command=self.text_input_playlist.xview, orient=tkinter.HORIZONTAL)
        scrollbar_text_input_h.place(x=20, y=145, width=440)

        self.text_input_playlist['yscrollcommand'] = scrollbar_text_input_v.set
        self.text_input_playlist['xscrollcommand'] = scrollbar_text_input_h.set

        self.music_folder_display = tkinter.StringVar()
        self.pic_folder_display = tkinter.StringVar()
        self.extra_music_file_display = tkinter.StringVar()

        self.entry_music_folder = ttk.Entry(self.root, textvariable=self.music_folder_display)
        self.entry_music_folder['state'] = 'readonly'
        self.entry_music_folder.place(x=170, y=180, width=245)

        self.entry_pic_folder = ttk.Entry(self.root, textvariable=self.pic_folder_display)
        self.entry_pic_folder['state'] = 'readonly'
        self.entry_pic_folder.place(x=170, y=210, width=245)

        self.entry_extra_music_file = ttk.Entry(self.root, textvariable=self.extra_music_file_display)
        self.entry_extra_music_file['state'] = 'readonly'
        self.entry_extra_music_file.place(x=170, y=240, width=190)

        self.music_folder_display.set(self.music_folder)
        self.pic_folder_display.set(self.pic_folder)
        self.extra_music_file_display.set(self.extra_music_file)

        lable_choose_music_folder = tkinter.Label(self.root, text='Music folder:')
        lable_choose_music_folder.place(x=30, y=180)

        lable_choose_pic_folder = tkinter.Label(self.root, text='Album picture folder:')
        lable_choose_pic_folder.place(x=30, y=210)

        lable_choose_extra_music_file = tkinter.Label(self.root, text='Extra music file:')
        lable_choose_extra_music_file.place(x=30, y=240)

        # 更换保存目录的按钮
        self.button_choose_music_folder = ttk.Button(self.root, text='Change', command=self.ask_for_music_folder)
        self.button_choose_music_folder.place(x=420, y=178, width=60)

        self.button_choose_pic_folder = ttk.Button(self.root, text='Change', command=self.ask_for_pic_folder)
        self.button_choose_pic_folder.place(x=420, y=208, width=60)

        self.button_choose_extra_music_file = ttk.Button(self.root, text='Change', command=self.ask_for_extra_music_file)
        self.button_choose_extra_music_file.place(x=420, y=238, width=60)

        self.button_edit_extra_music_file = ttk.Button(self.root, text='Edit', command=self.edit_extra_music_file)
        self.button_edit_extra_music_file.place(x=365, y=238, width=50)

        # 开始下载的按钮
        self.button_start_download = ttk.Button(self.root, text='Start downloading', width=30, command=self.start_download)
        self.button_start_download.place(x=250, y=280)

    def disable_widget(self):
        self.button_choose_extra_music_file['state'] = 'disable'
        self.button_choose_music_folder['state'] = 'disable'
        self.button_choose_pic_folder['state'] = 'disable'
        self.button_edit_extra_music_file['state'] = 'disable'
        self.button_start_download['state'] = 'disable'
        self.text_input_playlist['state'] = 'disable'
        self.root.protocol("WM_DELETE_WINDOW", self.diable_close_window)

    def enable_widget(self):
        self.button_choose_extra_music_file['state'] = 'normal'
        self.button_choose_music_folder['state'] = 'normal'
        self.button_choose_pic_folder['state'] = 'normal'
        self.button_edit_extra_music_file['state'] = 'normal'
        self.button_start_download['state'] = 'normal'
        self.text_input_playlist['state'] = 'normal'
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())

    def diable_close_window(self):
        pass

    def start_download(self):
        contents = self.text_input_playlist.get('1.0', tkinter.END).split('\n')
        self.disable_widget()
        self.progress_window = ProgressBarWindow(self.root)
        self.progress_window.place_widget()
        tools.progressbar_window = self.progress_window
        download_thread = DownloadThread({
            'playlists':contents,
            'music_folder':self.music_folder,
            'pic_folder':self.pic_folder,
            'extra_music_file':self.extra_music_file,
            'progressbar_window':self.progress_window,
            'callback':self.callback_thread
        })
        download_thread.start()

    def callback_thread(self,finished):
        if finished:
            self.progress_window.destory()
            self.finish_download()

    def finish_download(self):
        self.enable_widget()
        tools.progressbar_window = None
        messagebox.showinfo('', 'Download finished', parent=self.root)

    def mainloop(self):
        self.root.mainloop()


class DownloadThread(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.args = args
        self.progressbar_window = args['progressbar_window']

    def run(self):
        download_main.ne.set_wait_interval(1)
        for playlist in self.args['playlists']:
            if not playlist == '':
                download_main.download_playist(playlist, self.args['music_folder'], self.args['pic_folder'], self.args['extra_music_file'])
        
        self.args['callback'](True)
        raise SystemExit