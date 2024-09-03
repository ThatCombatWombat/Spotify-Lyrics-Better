import pygetwindow as gw
import win32gui
import time
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import simpledialog 
from threading import Thread

def list_running_apps():
    windows = gw.getAllWindows()
    apps = [(window._hWnd, window.title) for window in windows if window.title]  # Filter out empty titles
    return apps

def get_window_title_by_hwnd(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_lyrics(url):
    try:

        # Send a request to the Genius song page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with the id 'lyrics-root'
        lyrics_div = soup.find('div', id='lyrics-root')

        if lyrics_div:
            # Extract all text from the div, including text from span, br, and other tags
            lyrics = lyrics_div.get_text(separator='\n', strip=True)
            return lyrics if lyrics else "No lyrics found"
    except:
        return "Lyrics div not found"

def format_genius_url(artist_song):
    if ' - ' in artist_song:
        artist, song = artist_song.split(' - ', 1)
    else:
        return "Invalid format. Use 'Artist - Song'."
    
    artist_formatted = artist.replace(' ', '-')
    song_formatted = song.replace(' ', '-')
    url = f"https://genius.com/{artist_formatted}-{song_formatted}-lyrics"
    return url

class LyricsMonitorConsoleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyrics Monitor Console")
        
        self.console_text = tk.Text(root, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED, bg="#1e1e1e", fg="#dcdcdc", font=("Arial", 12))
        self.console_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring, bg="#4caf50", fg="white", font=("Arial", 12))
        self.start_button.pack(pady=10)
        
        self.update_app_list()
        self.lyrics_window = None
    
    def update_app_list(self):
        apps = list_running_apps()
        self.apps = apps
        
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.insert(tk.END, "Running applications:\n")
        for i, (hwnd, title) in enumerate(apps):
            self.console_text.insert(tk.END, f"{i + 1}. {title} (HWND: {hwnd})\n")
        self.console_text.config(state=tk.DISABLED)
    
    def start_monitoring(self):
        selected_index = self.ask_for_app_index()
        if selected_index is not None:
            selected_hwnd, selected_title = self.apps[selected_index]
            self.console_text.config(state=tk.NORMAL)
            self.console_text.insert(tk.END, f"\nMonitoring '{selected_title}'...\n")
            self.console_text.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)
            
            thread = Thread(target=self.monitor_app, args=(selected_hwnd,))
            thread.start()
        else:
            self.console_text.config(state=tk.NORMAL)
            self.console_text.insert(tk.END, "\nNo valid application selected.\n")
            self.console_text.config(state=tk.DISABLED)
    
    def ask_for_app_index(self):
        try:
            choice = simpledialog.askinteger("Select Application", "Enter the number of the app you want to monitor:", minvalue=1, maxvalue=len(self.apps))
            if choice is not None and 1 <= choice <= len(self.apps):
                return choice - 1
            else:
                return None
        except ValueError:
            return None
    
    def monitor_app(self, hwnd):
        previous_title = get_window_title_by_hwnd(hwnd)
        if previous_title:
            while True:
                current_title = get_window_title_by_hwnd(hwnd)
                if current_title and current_title != previous_title:
                    url = format_genius_url(current_title)
                    lyrics = get_lyrics(url)
                    self.update_console(f"Window title changed to: {current_title}\n")
                    self.update_console(f"URL: {url}\n")
                    self.update_lyrics_window(lyrics)
                    previous_title = current_title
                time.sleep(1)
            self.start_button.config(state=tk.NORMAL)
    
    def update_console(self, message):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, message)
        self.console_text.yview(tk.END)
        self.console_text.config(state=tk.DISABLED)
    
    def update_lyrics_window(self, lyrics):
        if self.lyrics_window:
            self.lyrics_window.update_lyrics(lyrics)
        else:
            self.lyrics_window = LyricsWindow(self.root, lyrics)
    
class LyricsWindow:
    def __init__(self, root, lyrics):
        self.lyrics_window = tk.Toplevel(root)
        self.lyrics_window.title("Lyrics")
        self.lyrics_window.geometry("800x1000")
        self.lyrics_window.configure(bg="black")
        self.lyrics_window.attributes('-transparentcolor', 'black')
        self.lyrics_window.attributes('-topmost', True)  # Keep window on top
        
        # Create a frame for lyrics with padding
        self.lyrics_frame = tk.Frame(self.lyrics_window, bg="black", padx=10, pady=10)
        self.lyrics_frame.pack(expand=True, fill=tk.BOTH)
        
        self.lyrics_text = tk.Text(self.lyrics_frame, wrap=tk.WORD, bg="black", fg="white", font=("Comfortaa", 24), borderwidth=0, highlightthickness=0)
        self.lyrics_text.pack(expand=True, fill=tk.BOTH)
        
        # Bind mouse events for window dragging
        self.lyrics_window.bind("<Button-1>", self.on_click)
        self.lyrics_window.bind("<B1-Motion>", self.on_drag)

        self.x = 0
        self.y = 0
        self.update_lyrics(lyrics)
    
    def on_click(self, event):
        self.x = event.x_root
        self.y = event.y_root

    def on_drag(self, event):
        delta_x = event.x_root - self.x
        delta_y = event.y_root - self.y
        
        new_x = self.lyrics_window.winfo_x() + delta_x
        new_y = self.lyrics_window.winfo_y() + delta_y
        self.lyrics_window.geometry(f"+{new_x}+{new_y}")
        
        self.x = event.x_root
        self.y = event.y_root
        
    def update_lyrics(self, lyrics):
        self.lyrics_text.config(state=tk.NORMAL)
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.insert(tk.END, lyrics)
        self.lyrics_text.config(state=tk.DISABLED)
        self.scroll_lyrics()
    
    def scroll_lyrics(self):
        try:

            lyrics = self.lyrics_text.get(1.0, tk.END)
            words = lyrics.split()
            num_words = len(words)

            if num_words == 0:
                return

            total_minutes = num_words / 120
            total_milliseconds = total_minutes * 60 * 1000
            num_visible_lines = int(self.lyrics_text.cget("height")) // 20
            line_height = self.lyrics_text.dlineinfo("1.0")[3]

            total_lines = int(len(words) / 5)
            scroll_rate = total_lines / total_minutes
            interval = int(60 * 1000 / scroll_rate)

            def scroll():
                self.lyrics_text.yview_scroll(1, "units")
                if self.lyrics_text.yview()[1] < 1.0:
                    self.lyrics_window.after(interval, scroll)

            self.lyrics_window.after(interval, scroll)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsMonitorConsoleApp(root)
    root.mainloop()
