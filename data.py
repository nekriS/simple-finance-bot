import json

def load_data(path_json): #загрузка json
    try:
        with open(path_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print(f'Файл {path_json} создан!')
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