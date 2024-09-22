import os
import json

# Путь к папке с песнями
folder_path = 'song'

# Список для хранения всех песен
SONGS = []

# Проходим по всем файлам в папке 'song'
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        # Открываем файл и читаем его содержимое
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            lyrics = file.read()
        
        # Формируем название песни без расширения файла
        title = os.path.splitext(filename)[0]
        
        # Добавляем песню в список
        SONGS.append({
            "title": title,
            "lyrics": lyrics
        })

# Преобразуем список в формат JSON (для наглядности или для записи в файл)
json_output = json.dumps(SONGS, ensure_ascii=False, indent=4)

# Сохраняем JSON в файл (если нужно)
with open('songs_data.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

# Выводим на экран результат
print(json_output)
