import json

def save_progress(song_title, wpm):
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
    except FileNotFoundError:
        progress = {"completed_songs": [], "wpm_records": {}}
    
    if song_title not in progress["completed_songs"]:
        progress["completed_songs"].append(song_title)
    
    if song_title not in progress["wpm_records"] or wpm > progress["wpm_records"][song_title]:
        progress["wpm_records"][song_title] = wpm
    
    with open('progress.json', 'w') as f:
        json.dump(progress, f)

def is_song_completed(song_title):
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
        return song_title in progress["completed_songs"]
    except FileNotFoundError:
        return False

def get_wpm_record(song_title):
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
        return progress["wpm_records"].get(song_title, 0)
    except FileNotFoundError:
        return 0

def reset_progress():
    with open('progress.json', 'w') as f:
        json.dump({"completed_songs": [], "wpm_records": {}}, f)