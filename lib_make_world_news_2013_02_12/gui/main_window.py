#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2013 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import threading, base64, heapq
import tkinter
from tkinter import ttk, scrolledtext, filedialog
from . import tk_mt, tk_async
from .. import fix_url, read_list, hashtag_replacer, make_world_news

DEFAULT_MAIN_WINDOW_WIDTH = 700
DEFAULT_MAIN_WINDOW_HEIGHT = 500

class MainWindow:
    def __init__(self):
        self._root = tkinter.Tk()
        self._tk_mt = tk_mt.TkMt(self._root)
        self._root.protocol('WM_DELETE_WINDOW', self._close_cmd)
        
        self._root.title('make-world-news-gui')
        self._root.geometry('{}x{}'.format(
                DEFAULT_MAIN_WINDOW_WIDTH, DEFAULT_MAIN_WINDOW_HEIGHT))
        
        self._menubar = tkinter.Menu(master=self._root)
        self._program_menu = tkinter.Menu(master=self._menubar)
        self._program_menu.add_command(label='New Data', command=self._new_data_cmd)
        self._program_menu.add_command(label='Transform', command=self._transform_cmd)
        self._program_menu.add_command(label='Load Hashtag Word List from File',
                command=self._load_hashtag_list_cmd)
        self._program_menu.add_command(label='Paste Input Messages',
                command=self._paste_in_msgs_cmd)
        self._program_menu.add_command(label='Copy Result',
                command=self._copy_result_cmd)
        self._program_menu.add_separator()
        self._program_menu.add_command(label='Close', command=self._close_cmd)
        self._menubar.add_cascade(label='Program', menu=self._program_menu)
        self._root.config(menu=self._menubar)
        
        self._top_frame = ttk.Frame(master=self._root)
        self._center_frame = ttk.Frame(master=self._root)
        self._bottom_frame = ttk.Frame(master=self._root)
        
        self._site_url_frame = ttk.Frame(master=self._top_frame)
        self._site_url_label = ttk.Label(master=self._site_url_frame,
                text='Site URL:')
        self._site_url_entry = ttk.Entry(master=self._site_url_frame)
        
        self._news_secret_key_frame = ttk.Frame(master=self._top_frame)
        self._news_secret_key_label = ttk.Label(master=self._news_secret_key_frame,
                text='News Secret Key:')
        self._news_secret_key_entry = ttk.Entry(master=self._news_secret_key_frame)
        
        self._options_frame = ttk.Frame(master=self._top_frame)
        self._use_short_var = tkinter.BooleanVar(value=True)
        self._use_short_button = ttk.Checkbutton(
                master=self._options_frame,
                variable=self._use_short_var,
                text='Use Short Links',
                )
        
        self._hashtag_list_frame = ttk.Frame(master=self._top_frame)
        self._hashtag_list_label = ttk.Label(master=self._hashtag_list_frame,
                text='Hashtag Word List:')
        self._hashtag_list_entry = ttk.Entry(master=self._hashtag_list_frame)
        
        self._text = scrolledtext.ScrolledText(master=self._center_frame)
        self._text.propagate(False)
        
        self._new_data_button = ttk.Button(master=self._bottom_frame,
                text='New Data',
                command=self._new_data_cmd)
        self._new_data_button.config(state=tkinter.DISABLED)
        self._transform_button = ttk.Button(master=self._bottom_frame,
                text='Transform',
                command=self._transform_cmd)
        
        self._paste_in_msgs_button = ttk.Button(master=self._bottom_frame,
                text='Paste Input Messages',
                command=self._paste_in_msgs_cmd)
        self._copy_result_button = ttk.Button(master=self._bottom_frame,
                text='Copy Result',
                command=self._copy_result_cmd)
        self._copy_result_button.config(state=tkinter.DISABLED)
        self._close_button = ttk.Button(master=self._bottom_frame,
                text='Close',
                command=self._close_cmd)
        
        self._status_var = tkinter.StringVar()
        self._statusbar = ttk.Label(master=self._bottom_frame,
                textvariable=self._status_var)
        
        self._site_url_label.pack(side=tkinter.LEFT,padx=10, pady=10)
        self._site_url_entry.pack(fill=tkinter.X, padx=10, pady=10)
        self._site_url_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        self._news_secret_key_label.pack(side=tkinter.LEFT, padx=10, pady=10)
        self._news_secret_key_entry.pack(fill=tkinter.X, padx=10, pady=10)
        self._news_secret_key_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        self._use_short_button.pack(side=tkinter.LEFT, padx=10, pady=10)
        self._options_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        self._hashtag_list_label.pack(side=tkinter.LEFT, padx=10, pady=10)
        self._hashtag_list_entry.pack(fill=tkinter.X, padx=10, pady=10)
        self._hashtag_list_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self._text.pack(fill=tkinter.BOTH, expand=True)
        
        self._new_data_button.pack(side=tkinter.LEFT, padx=10, pady=10)
        self._transform_button.pack(side=tkinter.LEFT, padx=10, pady=10)
        self._statusbar.pack(side=tkinter.LEFT, expand=True, padx=10, pady=10)
        
        self._close_button.pack(side=tkinter.RIGHT, padx=10, pady=10)
        self._copy_result_button.pack(side=tkinter.RIGHT, padx=10, pady=10)
        self._paste_in_msgs_button.pack(side=tkinter.RIGHT, padx=10, pady=10)
        
        self._top_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        self._center_frame.pack(fill=tkinter.BOTH, expand=True)
        self._bottom_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        
        self._result_state = False
        self._busy_state = False
        self._busy_state_id = object()
        self._set_status('Ready')
    
    def _close_cmd(self):
        if self._busy_state:
            self._root.bell()
            return
        
        self._tk_mt.push_destroy()
    
    def _set_status(self, text):
        self._status_var.set('Status: {}'.format(text))
    
    def _new_data_cmd(self):
        if self._busy_state or not self._result_state:
            self._root.bell()
            return
        
        self._result_state = False
        self._set_status('Ready')
        
        self._new_data_button.config(state=tkinter.DISABLED)
        self._copy_result_button.config(state=tkinter.DISABLED)
        self._site_url_entry.config(state=tkinter.NORMAL)
        self._news_secret_key_entry.config(state=tkinter.NORMAL)
        self._use_short_button.config(state=tkinter.NORMAL)
        self._hashtag_list_entry.config(state=tkinter.NORMAL)
        self._text.config(state=tkinter.NORMAL)
        self._transform_button.config(state=tkinter.NORMAL)
        self._paste_in_msgs_button.config(state=tkinter.NORMAL)
        
        self._text.delete('1.0', tkinter.END)
    
    def _transform_cmd(self):
        if self._busy_state or self._result_state:
            self._root.bell()
            return
        
        site_url = self._site_url_entry.get().strip()
        news_secret_key_b64 = self._news_secret_key_entry.get().strip()
        use_short = self._use_short_var.get()
        hashtag_list_str = self._hashtag_list_entry.get().strip()
        in_msg_text = self._text.get('1.0', tkinter.END).strip()
        
        site_url = fix_url.fix_url(site_url)
        
        try:
            news_secret_key = base64.b64decode(news_secret_key_b64.encode())
        except ValueError:
            news_secret_key = None
        
        if hashtag_list_str:
            other_word_func_factory = hashtag_replacer.create_word_func_factory(
                    hashtag_list_str.split(),
                    )
        else:
            other_word_func_factory = None
        
        in_msg_list = tuple(filter(
                None,
                map(
                        lambda s: s.strip(),
                        in_msg_text.split('\n'),
                        ),
                ))
        
        if not in_msg_list or not site_url or not news_secret_key:
            self._root.bell()
            return
        
        self._result_state = True
        self._busy_state = True
        self._busy_state_id = object()
        self._set_status('Working')
        
        self._text.delete('1.0', tkinter.END)
        
        self._site_url_entry.config(state=tkinter.DISABLED)
        self._news_secret_key_entry.config(state=tkinter.DISABLED)
        self._use_short_button.config(state=tkinter.DISABLED)
        self._hashtag_list_entry.config(state=tkinter.DISABLED)
        self._text.config(state=tkinter.DISABLED)
        self._new_data_button.config(state=tkinter.DISABLED)
        self._transform_button.config(state=tkinter.DISABLED)
        self._paste_in_msgs_button.config(state=tkinter.DISABLED)
        self._copy_result_button.config(state=tkinter.DISABLED)
        self._close_button.config(state=tkinter.DISABLED)
        
        busy_state_id = self._busy_state_id
        out_heap = []
        
        def on_result(err, data):
            self._tk_mt.push(lambda: self._on_transform_result(err, busy_state_id, out_heap, data))
        
        def on_done(err):
            self._tk_mt.push(lambda: self._on_transform_done(err, busy_state_id, out_heap))
        
        make_world_news.make_world_news(
                in_msg_list,
                site_url,
                news_secret_key,
                use_short=use_short,
                other_word_func_factory=other_word_func_factory,
                on_result=on_result,
                callback=on_done,
                )
    
    def _on_transform_result(self, err, busy_state_id, out_heap, data):
        if not self._busy_state or busy_state_id != self._busy_state_id:
            return
        
        if err is not None:
            return
        
        heapq.heappush(out_heap, (data.msg_id, data))
    
    def _on_transform_done(self, err, busy_state_id, out_heap):
        if not self._busy_state or busy_state_id != self._busy_state_id:
            return
        
        if err is not None:
            return
        
        while True:
            try:
                msg_id, data = heapq.heappop(out_heap)
            except IndexError:
                break
            
            self._text.config(state=tkinter.NORMAL)
            self._text.insert(tkinter.END, '{}\n'.format(data.result))
            self._text.config(state=tkinter.DISABLED)
        
        self._busy_state = False
        self._busy_state_id = object()
        self._set_status('Done')
        
        self._new_data_button.config(state=tkinter.NORMAL)
        self._copy_result_button.config(state=tkinter.NORMAL)
        self._close_button.config(state=tkinter.NORMAL)
    
    def _load_hashtag_list_result(self, err, busy_state_id, result):
        if self._busy_state or busy_state_id != self._busy_state_id or self._result_state:
            return
        
        if err or not result:
            return
        
        hashtag_list_path = str(result)
        try:
            hashtag_list = read_list.read_list(hashtag_list_path, read_words=True)
            hashtag_list_str = ' '.join(hashtag_list)
        except Exception:
            self._root.bell()
            return
        
        self._hashtag_list_entry.delete(0, tkinter.END)
        self._hashtag_list_entry.insert(0, hashtag_list_str)
    
    def _load_hashtag_list_cmd(self):
        if self._busy_state or self._result_state:
            self._root.bell()
            return
        
        tk_async.tk_async(
                self._root,
                lambda: filedialog.askopenfilename(parent=self._root),
                self._busy_state_id,
                callback=self._load_hashtag_list_result,
                )
    
    def _paste_in_msgs_cmd(self):
        if self._busy_state or self._result_state:
            self._root.bell()
            return
        
        content = self._root.clipboard_get()
        self._text.delete('1.0', tkinter.END)
        self._text.insert(tkinter.END, content)
    
    def _copy_result_cmd(self):
        if self._busy_state or not self._result_state:
            self._root.bell()
            return
        
        content = self._text.get('1.0', tkinter.END).rstrip()
        self._root.clipboard_clear()
        self._root.clipboard_append(content)
