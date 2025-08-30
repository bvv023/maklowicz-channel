import subprocess
import os
import json
from datetime import datetime

# -----------------------------
# Налаштування проекту
# -----------------------------
folder = r"C:\Users\User\OneDrive\GoIT\Work\maklowicz-channel"
os.makedirs(folder, exist_ok=True)

playlist_file = os.path.join(folder, "maklowicz_youtube.m3u")
archive_file = os.path.join(folder, "archive.txt")

channel_url = "https://www.youtube.com/@Robert_Maklowicz"

print(f"[INFO] Плейлист буде створено тут: {playlist_file}")

# -----------------------------
# Читаємо архів вже доданих відео
# -----------------------------
if os.path.exists(archive_file):
    with open(archive_file, "r", encoding="utf-8") as f:
        archived = set(f.read().splitlines())
else:
    archived = set()

# -----------------------------
# Отримуємо список відео з каналу
# -----------------------------
try:
    result = subprocess.run(
        ["python", "-m", "yt_dlp", "-j", "--flat-playlist", channel_url],
        capture_output=True,
        text=True,
        check=True
    )
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Не вдалося отримати відео: {e}")
    exit(1)

lines = result.stdout.strip().split("\n")
video_data = []
for line in lines:
    if line.strip():
        try:
            video_data.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # пропускаємо некоректні рядки

# -----------------------------
# Формуємо список відео
# -----------------------------
video_list = []
new_links = []

for video in video_data:
    vid_id = video.get("id")
    title = video.get("title", "No title")
    upload_date = video.get("upload_date")
    link = f"https://www.youtube.com/watch?v={vid_id}"
    dt = datetime.strptime(upload_date, "%Y%m%d") if upload_date else datetime.min
    video_list.append((link, title, dt))
    if link not in archived:
        new_links.append((link, title))
        archived.add(link)

# -----------------------------
# Сортуємо відео найновіші зверху
# -----------------------------
video_list.sort(key=lambda x: x[2], reverse=True)

# -----------------------------
# Оновлюємо архів
# -----------------------------
with open(archive_file, "w", encoding="utf-8") as f:
    for link, _, _ in video_list:
        f.write(link + "\n")

# -----------------------------
# Генеруємо плейлист .m3u
# -----------------------------
with open(playlist_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for link, title, _ in video_list:
        f.write(f"#EXTINF:-1,{title}\n")
        f.write(link + "\n\n")

print(f"[INFO] Плейлист {playlist_file} оновлено. Нових відео додано: {len(new_links)}")

# -----------------------------
# Автоматичний пуш у GitHub
# -----------------------------
try:
    subprocess.run(["git", "add", "maklowicz_youtube.m3u"], cwd=folder, check=True)
    subprocess.run(["git", "commit", "-m", "Update Maklowicz playlist"], cwd=folder, check=True)
    subprocess.run(["git", "push"], cwd=folder, check=True)
    print("[INFO] Плейлист успішно запушений у GitHub")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Помилка при пуші у GitHub: {e}")
