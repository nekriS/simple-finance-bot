import os
import datetime
import json

def log(text):

    if text != "" and text != " ":
        # Получаем сегодняшнюю дату в формате YYYY-MM-DD
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Создаем путь к каталогу и файлу
        log_directory = 'log'
        log_file_name = f'log_{today_date}.txt'
        log_file_path = os.path.join(log_directory, log_file_name)

        # Проверяем наличие каталога "log" и создаем его, если его нет
        create_folder(log_directory)

        # Формируем строку для записи: "дата-время > текст"
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"{today_date} {current_time} > {text}"

        # Проверяем existence файла и записываем данные
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(log_entry+"\n")
        try:
            print(log_entry)
        except:
            print(log_entry.encode("utf-8"))


def create_folder(folder):
    if not os.path.isdir(f"{folder}"):
        os.mkdir(folder)
        log(f"Folder {folder} was created!")

def create_hierarchy(hierarchy, path=""):
    if isinstance(hierarchy, dict):
        for key in hierarchy.keys():
            create_folder(f"{path}{key}")
            create_hierarchy(hierarchy[key], path=f"{path}{key}/")


def load_data(path_json): #загрузка json
    try:
        with open(path_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print(f'File {path_json} was created!')
        data = {}
        with open(path_json, "w", encoding='utf-8') as f:
            f.write(json.dumps(data, indent=4))
    finally:
        f.close()
    return data


def save_data(data, path_json): #сохранить json
    with open(path_json, "w", encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))
    f.close()
            










