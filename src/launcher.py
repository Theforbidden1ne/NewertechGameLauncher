import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import subprocess
import threading
import zipfile

# --- UI CONSTANTS ---
BG_COLOR = "#1e1e1e"      # Dark Gray
CARD_COLOR = "#2d2d2d"    # Lighter Gray
ACCENT_COLOR = "#0078d7"  # Windows Blue
TEXT_COLOR = "#ffffff"
SUCCESS_COLOR = "#28a745" # Green for Play

class ModernUnityLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Newertech Game Store")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)
        
        self.install_dir = os.path.join(os.getcwd(), "installed_games")
        if not os.path.exists(self.install_dir):
            os.makedirs(self.install_dir)

        # Scrollable Area Setup
        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=580)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10)
        self.scrollbar.pack(side="right", fill="y")

        self.fetch_games()

    def fetch_games(self):
        try:
            # Replace with your actual server IP if not local
            response = requests.get("IP/games", timeout=3)
            games = response.json()
            for game in games:
                self.add_game_card(game)
        except Exception:
            err = tk.Label(self.scrollable_frame, text="Could not connect to store server.", 
                          bg=BG_COLOR, fg="red", font=("Segoe UI", 10))
            err.pack(pady=20)

    def add_game_card(self, game):
        # Game Card Container
        card = tk.Frame(self.scrollable_frame, bg=CARD_COLOR, pady=15, padx=15)
        card.pack(fill="x", pady=10, padx=20)

        # Game Title
        title = tk.Label(card, text=game['name'].upper(), font=("Segoe UI", 12, "bold"), 
                        bg=CARD_COLOR, fg=TEXT_COLOR)
        title.pack(side="left")

        # Status Label (Installed vs Not)
        game_folder = os.path.join(self.install_dir, game['name'])
        is_installed = os.path.exists(os.path.join(game_folder, game['exe_name']))

        # Action Button
        btn_text = "PLAY" if is_installed else "DOWNLOAD"
        btn_color = SUCCESS_COLOR if is_installed else ACCENT_COLOR
        
        btn = tk.Button(card, text=btn_text, bg=btn_color, fg="white", 
                        font=("Segoe UI", 9, "bold"), width=12, relief="flat",
                        command=lambda g=game: self.handle_action(g, btn, progress))
        btn.pack(side="right", padx=10)

        # Progress Bar (Hidden initially)
        progress = ttk.Progressbar(card, orient="horizontal", length=150, mode='determinate')
        progress.pack(side="right", padx=10)
        if is_installed:
            progress.pack_forget() # Hide if already installed

    def handle_action(self, game, button, progress_bar):
        game_folder = os.path.join(self.install_dir, game['name'])
        exe_path = os.path.join(game_folder, game['exe_name'])

        if os.path.exists(exe_path):
            # LOCAL CHECK PASSED: Just Launch
            subprocess.Popen([exe_path], cwd=game_folder)
        else:
            # DOWNLOAD REQUIRED
            button.config(state="disabled", text="INSTALLING...")
            progress_bar.pack(side="right", padx=10)
            threading.Thread(target=self.download_and_extract, args=(game, button, progress_bar)).start()

    def download_and_extract(self, game, button, progress_bar):
        game_folder = os.path.join(self.install_dir, game['name'])
        zip_path = os.path.join(self.install_dir, game['filename'])
        
        try:
            # 1. Download
            url = f"IP/download/{game['filename']}"
            r = requests.get(url, stream=True)
            total = int(r.headers.get('content-length', 0))
            
            with open(zip_path, 'wb') as f:
                done = 0
                for chunk in r.iter_content(chunk_size=1024*64):
                    f.write(chunk)
                    done += len(chunk)
                    progress_bar['value'] = (done / total) * 100

            # 2. Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(game_folder)
            
            os.remove(zip_path) # Clean up zip

            # 3. Update UI to "PLAY" mode
            self.root.after(0, lambda: self.finalize_install(button, progress_bar))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Install failed: {e}"))
            self.root.after(0, lambda: button.config(state="normal", text="RETRY"))

    def finalize_install(self, button, progress_bar):
        progress_bar.pack_forget()
        button.config(state="normal", text="PLAY", bg=SUCCESS_COLOR)
        messagebox.showinfo("Success", "Game ready to play!")

if __name__ == "__main__":
    # Customizing the Progress Bar style to look sleeker
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=10, background=ACCENT_COLOR, troughcolor=CARD_COLOR, borderwidth=0)
    
    app = ModernUnityLauncher(root)
    root.mainloop()
