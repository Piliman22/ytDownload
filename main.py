import os
import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread
import yt_dlp
from datetime import datetime
import csv
import requests

class DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube ダウンローダー")
        master.geometry("750x700")
        master.configure(bg="#fafafa")  # ライトグレーの背景色

        self.url_label = tk.Label(master, text="YouTube URL:", bg="#fafafa", fg="#333", font=("Roboto", 12))
        self.url_label.grid(row=0, column=0, sticky=tk.W)

        self.url_entry = tk.Entry(master, width=40, font=("Roboto", 10))
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=10)

        self.format_label = tk.Label(master, text="フォーマット:", bg="#fafafa", fg="#333", font=("Roboto", 12))
        self.format_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.format_var = tk.StringVar(master)
        self.format_var.set("mp3")  # デフォルトのフォーマット
        self.format_menu = tk.OptionMenu(master, self.format_var, "mp3", "wav")
        self.format_menu.config(bg="#fafafa", fg="#333", font=("Roboto", 10))
        self.format_menu.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=10)

        self.progress_label = tk.Label(master, text="", bg="#fafafa", fg="#333", font=("Roboto", 10))
        self.progress_label.grid(row=2, column=0, columnspan=3, pady=5, padx=10)

        self.download_button = tk.Button(master, text="ダウンロード", command=self.start_download, bg="#2979ff", fg="white", font=("Roboto", 12), relief=tk.FLAT)
        self.download_button.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=10, padx=10)

        self.history_label = tk.Label(master, text="ダウンロード履歴", bg="#fafafa", fg="#333", font=("Roboto", 12))
        self.history_label.grid(row=4, column=0, columnspan=3, pady=5, padx=10)

        self.history_tree = ttk.Treeview(master, columns=("URL", "フォーマット", "日時"), show="headings")
        self.history_tree.heading("URL", text="URL")
        self.history_tree.heading("フォーマット", text="フォーマット")
        self.history_tree.heading("日時", text="日時")
        self.history_tree.grid(row=5, column=0, columnspan=3, pady=5, padx=10)
        self.load_history()  # 履歴を読み込む

        self.history_tree.bind("<Double-1>", self.redownload_selected)  # 履歴をダブルクリックした時に再ダウンロード

        self.delete_button = tk.Button(master, text="削除", command=self.delete_selected, bg="#ff3d00", fg="white", font=("Roboto", 12), relief=tk.FLAT)
        self.delete_button.grid(row=6, column=0, columnspan=3, sticky=tk.EW, pady=10, padx=10)

    def start_download(self):
        url = self.url_entry.get()
        format = self.format_var.get()

        if not url:
            messagebox.showerror("エラー", "YouTubeのURLを入力してください")
            return

        download_thread = Thread(target=self.download, args=(url, format))
        download_thread.start()

    def download(self, url, format):
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'%(title)s_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.{format}',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
            'progress_hooks': [self.show_progress],
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                ydl.download([url])
                self.update_history(url, format)  # ダウンロード完了後、履歴を更新
                messagebox.showinfo("成功", "ダウンロードが正常に完了しました！")
            except Exception as e:
                messagebox.showerror("エラー", f"エラーが発生しました：{str(e)}")

    def show_progress(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            speed = d['_speed_str']
            eta = d['_eta_str']
            self.progress_label.config(text=f"ダウンロード中 {percent} 進行中 {speed}、ETA: {eta}", font=("Roboto", 10))
        elif d['status'] == 'finished':
            self.progress_label.config(text="ダウンロード完了", font=("Roboto", 10))
        elif d['status'] == 'error':
            self.progress_label.config(text="ダウンロードエラー", font=("Roboto", 10))

    def update_history(self, url, format):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_tree.insert("", "end", values=(url, format, now))
        self.save_history()  # 履歴を保存

    def load_history(self):
        if os.path.exists("history.csv"):
            with open("history.csv", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    self.history_tree.insert("", "end", values=row)

    def save_history(self):
        with open("history.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for row_id in self.history_tree.get_children():
                row = self.history_tree.item(row_id)['values']
                writer.writerow(row)

    def delete_selected(self):
        selected_item = self.history_tree.selection()
        if selected_item:
            self.history_tree.delete(selected_item)
            self.save_history()  # 履歴を保存

    def redownload_selected(self, event):
        selected_item = self.history_tree.selection()
        if selected_item:
            url = self.history_tree.item(selected_item)['values'][0]
            format = self.history_tree.item(selected_item)['values'][1]
            self.start_download(url, format)

root = tk.Tk()
app = DownloaderApp(root)
response = requests.get("https://github.com/Piliman22/ytDownload/blob/main/favicon.ico?raw=true")

with open("favicon.ico", "wb") as f:
    f.write(response.content)

root.iconbitmap("favicon.ico")

root.mainloop()

