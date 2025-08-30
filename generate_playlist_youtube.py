import subprocess
import os
import json
from datetime import datetime

# Папка проекту
folder = r"C:\Users\User\OneDrive\GoIT\Work\maklowicz-channel"
os.makedirs(folder, exist_ok=True)

playlist_file = os.path.join(folder, "maklowicz_youtube.m3u")
archive_file = os.path.join(folder, "archive.txt")

channel_url = "https://www.youtube.com/@Robert_Maklowicz"

# Читаємо архів
if os.path.exists(archive_file):
    with open(archive_file, "r", encoding="utf-8") as f:
        archived = set(f.read().splitlines())
else:
    archived = set()

# Отримуємо всі відео з каналу
result = subprocess.run(
    ["python", "-m", "yt_dlp", "-j", "--flat-playlist", channel_url],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split("\n")
video_data = [json.loads(line) for line in lines]

video_list = []
new_links = []

for video in video_data:
    vid_id = video.get("id")
    title = video.get("title")
    upload_date = video.get("upload_date")
    link = f"https://www.youtube.com/watch?v={vid_id}"
    dt = datetime.strptime(upload_date, "%Y%m%d") if upload_date else datetime.min
    video_list.append((link, title, dt))
    if link not in archived:
        new_links.append((link, title))
        archived.add(link)

# Сортуємо найновіші зверху
video_list.sort(key=lambda x: x[2], reverse=True)

# Оновлюємо архів
with open(archive_file, "w", encoding="utf-8") as f:
    for link, _, _ in video_list:
        f.write(link + "\n")

# Генеруємо плейлист
with open(playlist_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for link, title, _ in video_list:
        f.write(f"#EXTINF:-1,{title}\n")
        f.write(link + "\n\n")

# Автоматичний пуш у GitHub
subprocess.run(["git", "add", "maklowicz_youtube.m3u"], cwd=folder)
subprocess.run(["git", "commit", "-m", "Update Maklowicz playlist"], cwd=folder)
subprocess.run(["git", "push"], cwd=folder)

print(f"Плейлист {playlist_file} оновлено. Нових відео додано: {len(new_links)}")
