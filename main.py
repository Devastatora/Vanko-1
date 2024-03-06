import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from pytube import YouTube
import os
from youtubesearchpython import VideosSearch
import time
import json
import requests
import base64
import sys
from tkinter import PhotoImage


destination_variable = None
last_key_press_time = 0


file_url = "https://drive.usercontent.google.com/u/0/uc?id=1G8A_dexq9hZnxE1SoPW-_1CSx5SNTmXJ&export=download"  # Replace this with the link to your ip.txt file
response = requests.get(file_url)  # Send a request to the link
allowed_ip_addresses = response.text  # Get the contents of the file as a string
allowed_ip_addresses = allowed_ip_addresses.split("\n")



def ip_to_int(ip):
    # Convert an IP address to an integer
    # Source: https://stackoverflow.com/a/561704/13664177
    o = list(map(int, ip.split('.')))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res
# Convert the IP addresses in the list to integers
allowed_ip_addresses = [ip_to_int(ip) for ip in allowed_ip_addresses]

def check_access():
    # Get the IP address of the device

    ip_address = requests.get('https://api.ipify.org').text
    ip_address = ip_to_int(ip_address)


    # Check if the IP address is in the list of allowed addresses
    if ip_address in allowed_ip_addresses:

        return True  # Access is allowed
    else:
        return False  # Access is denied




def get_latest_release(repo_url):
    owner, repo = repo_url.split('/')[-2:]
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", headers={"Authorization": "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"})
    if response.status_code == 200:
        data = response.json()
        latest_version = data['tag_name']
        return latest_version
    else:
        return None
def compare_versions(current_version, latest_version):
        if current_version < latest_version:
            return True  # New version available
        else:
            return False  # Up-to-date




class AutocompleteEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()
        self.suggestions = []
        self.popup_menu = tk.Menu(self, font=("Arial", 35), tearoff=60)
        self.bind('<KeyRelease>', self.schedule_search)
        self.last_key_press_time = 0  # Add this line to initialize last_key_press_time
        self.bind('<Return>', self.update_suggestions)

    def schedule_search(self, event):
        # Update the last key press time
        self.last_key_press_time = time.time()

        # Schedule the perform_search method to be called after 5 seconds of inactivity
        self.after(3000, self.perform_search)

    def perform_search(self):
        # Check if at least 5 seconds have passed since the last key press
        if time.time() - self.last_key_press_time >= 3:
            # Get the text from the entry and perform the search
            text = self.get()
            if len(text) >= 3:
                self.update_suggestions()
    def update_suggestions(self, *args):
        text = self.var.get()
        if len(text) >= 3:  # Only search for suggestions when at least 5 characters are entered
            self.suggestions = self.get_suggestions(text)
            if self.popup_menu:
                self.popup_menu.destroy()
            self.popup_menu = tk.Menu(self)
            for suggestion in self.suggestions:
                self.popup_menu.add_command(label=suggestion, command=lambda s=suggestion: self.var.set(s))
            self.popup_menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())

    def get_suggestions(self, text):
        # Implement your logic to get suggestions based on the entered text
        # You can use the 'youtubesearchpython' library to search for videos and return their titles as suggestions
        videos = VideosSearch(text, limit=5).result()
        if videos['result']:
            return [video['title'] for video in videos['result']]
        return []
def download_mp3(url, destination='.'):
    global destination_variable
    if not url:
        # If the field is empty, show a message and return
        messagebox.showwarning("Празно поле", "Моля въведете име на песен или линк от Youtube!")
        return
    try:
        if not url.startswith("http"):
            # If the URL is not provided, search for the song and get the URL
            videos = VideosSearch(url, limit=1).result()
            if videos['result']:
                url = videos['result'][0]['link']
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        destination_folder = destination_variable.get() if isinstance(destination_variable,
                                                                      tk.StringVar) else destination_variable

        base, ext = os.path.splitext(audio_stream.title)
        new_file = os.path.join(destination_folder, base + '.mp3')

        # Check if the file already exists
        counter = 1
        while os.path.exists(new_file):
            new_file = os.path.join(destination_folder, f"{base} ({counter}).mp3")
            counter += 1

        audio_stream.download(output_path=destination_folder)
        os.rename(os.path.join(destination_folder, audio_stream.default_filename), new_file)
        messagebox.showinfo("Сваляне завършено", "Файлът беше успешно свален.")
        return new_file
    except Exception as e:
        messagebox.showerror("Грешка", f"Грешка при свалянето: {str(e)}")
        return None

def choose_destination():
    global destination_variable
    chosen_folder = filedialog.askdirectory()
    destination_variable.set(chosen_folder)

    # Save the selected folder path to a file
    with open('destination_folder.json', 'w') as file:
        json.dump(chosen_folder, file)
def paste_url(root):
    clipboard_text = root.clipboard_get()
    if clipboard_text.startswith("http"):
        url_entry.delete(0, tk.END)
        url_entry.insert(0, clipboard_text)
    else:
        search_song(clipboard_text)

def search_song(song_name):
    videos = VideosSearch(song_name, limit=5).result()
    # Here, you can process the videos and display the results in the graphical interface
    print(videos)  # Example of printing the results in the console
    if videos['result']:
        url_entry.delete(0, tk.END)
        url_entry.insert(0, videos['result'][0]['link'])

def search_live():
    search_text = url_entry.get()
    if not search_text:
        # If the field is empty, show a message and return
        messagebox.showwarning("Празно поле", "Моля въведете име на песен или линк от Youtube!")
        return
    search_text = url_entry.get()
    if search_text.startswith("http"):
        download_mp3(search_text, destination_variable)
    else:
        search_song(search_text)



def main():
    # Проверка на достъпа
    if not check_access():
        # Показване на съобщение за грешка
        messagebox.showerror("Грешка", "Нямате достъп до това приложение!")

        # Прекратяване на програмата
        exit()
    repo_url = "https://github.com/Devastatora/Vanko-1"
    latest_version = get_latest_release(repo_url)
    print(f"The latest version of the repository is: {latest_version}")
    global destination_variable
    global url_entry
    root = tk.Tk()
    root.title("*DJ IWAN KALEW*")
    root.geometry("600x300")  # Increased the size of the window
    root.configure(bg="#999966")  # Grey background
    icon = PhotoImage(file="icon.png")
    root.iconphoto(False, icon)


    # Center the window on the screen
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    position_right = int(root.winfo_screenwidth() / 3 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(f"+{position_right}+{position_down}")
    with open('version.txt', 'r') as file:
        current_version = file.read().strip()

    # Get the latest version from GitHub
    latest_version = get_latest_release("https://github.com/Devastatora/Vanko-1")

    # Compare the versions
    if latest_version and compare_versions(current_version, latest_version):
        # Display update notification
        messagebox.showinfo("Update Available",
                            "A new version is available! Please update your application to the latest version.")

    url_label = tk.Label(root, text="Линк или Име на песента:", bg="#999966", fg="#ffffcc",font=("Arial", 15))
    url_label.pack(pady=5)
    url_entry = AutocompleteEntry(root, width=50, font=("Arial", 15), bd=3, relief="groove")
    url_entry.pack()

    paste_button = tk.Button(root, text="Постави URL", command=lambda: paste_url(root), bg="#f2f2f2", fg="#000000",
                             font=("Arial", 10), activebackground="#999966")
    paste_button.pack(pady=10)

    destination_label = tk.Label(root, text="Запази в:", bg="#999966", fg="#ffffcc", font=("Arial", 15))
    destination_label.pack(pady=0)
    destination_variable = tk.StringVar(root, value=os.getcwd())
    if os.path.exists('destination_folder.json'):
        with open('destination_folder.json', 'r') as file:
            destination_variable.set(json.load(file))

    destination_entry = tk.Entry(root, textvariable=destination_variable,font=("Arial", 15), bd=3, relief="groove")
    destination_entry.pack()
    destination_button = tk.Button(root, text="Избери папка", command=choose_destination, bg="#f2f2f2", fg="#000000",
                                   font=("Arial", 10))
    destination_button.pack(pady=5)

    download_button = tk.Button(root, text="Изтегли",
                                command=lambda: download_mp3(url_entry.get(), destination_variable), bg="#66ffff",
                                fg="#000000", font=("Arial", 20, "bold"))
    download_button.pack(pady=10)

    root.mainloop()
if __name__ == "__main__":
    main()
