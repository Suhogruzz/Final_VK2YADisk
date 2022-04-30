import requests
import json
import PySimpleGUI as sg
import configparser
import time

# Загрузка настроек из файла settings.ini
config = configparser.ConfigParser()
config.read("settings.ini")


class DownloadFromVk:

    def __init__(self, user_id, token: str, yadisk: str):
        self.user_id = user_id
        self.token = token
        self.yadisk = yadisk
        self.file_path = ya_disk_path
        self.api_version = config['vk_api']['api_version']
        self.get_photos_method_url = config['vk_api']['get_photos_method_url']
        self.upload_url_api = config['yadisk_api']['upload_url_api']
        self.mkdir_url = config['yadisk_api']['mkdir_url']

# Получение данных о фото с VK, создание названия файла и загрузка их на YADisk.
# GUI с прогресс-баром загрузки и popup окном выбора количества фото
    def upload_photos(self, user_id):
        names_list = []
        logs_list = []
        yaheaders = {'Content-Type': 'application/json',
                     'Authorization': self.yadisk}
        vkparams = {'access_token': self.token,
                    'v': self.api_version,
                    'album_id': 'profile',
                    'owner_id': user_id,
                    'extended': True,
                    'photo_sizes': True
                    }
        response = requests.get(self.get_photos_method_url, params=vkparams)
        profile_list = response.json()
        amount_to_download = int(sg.popup_get_text(f"Обнаружено {profile_list['response']['count']} фото",
                                                   default_text='Сколько фото скачать?'
                                                   ))
        if amount_to_download in range(0, profile_list['response']['count']):
            profile_list['response']['count'] = amount_to_download
            count = amount_to_download
            i = 0
            for file in profile_list['response']['items']:
                sg.one_line_progress_meter('Процесс загрузки',
                                           i+1,
                                           amount_to_download,
                                           'Загружено фото:',
                                           )
                time.sleep(3)
                self.size = file['sizes'][-1]['type']
                photo_url = file['sizes'][-1]['url']
                file_name = file['likes']['count']
                if file_name not in names_list:
                    names_list.append(file_name)
                else:
                    file_name = str(file['likes']['count']) + str(file['date'])
                    names_list.append(file_name)
                download_photo = requests.get(photo_url)
                yaparams = {'path': f'{self.file_path}/{file_name}'}
                get_upload_url = requests.get(self.upload_url_api, headers=yaheaders, params=yaparams)
                get_url = get_upload_url.json()
                upload_url = get_url['href']
                file_upload = requests.put(upload_url, download_photo)
                status = file_upload.status_code
                download_log = {'file_name': file_name, 'size': self.size}
                logs_list.append(download_log)
                i += 1
                count -= 1
                if count == 0:
                    break
            with open('log.json', 'a') as file:
                json.dump(logs_list, file, indent=2)

            if 500 > status != 400:
                success_popup()
            else:
                error_popup()
        elif amount_to_download is None:
            pass
        else:
            new_upload.upload_photos(new_upload.user_id)

# Создание папки на YADisk
    def create_folder(self):
        params = {'path': self.file_path}
        headers = {'Content-Type': 'application/json',
                   'Authorization': self.yadisk}
        requests.api.put(self.mkdir_url, headers=headers, params=params)


# GUI с вводом начальных параметров программы
def init_input():
    global ya_disk_token, vk_token, vk_user_id, ya_disk_path
    layout = [[sg.Text('Введите VKid')],
              [sg.InputText()],
              [sg.Text('Введите OAuth токен с Полигона')],
              [sg.InputText()],
              [sg.Text('Введите токен VK')],
              [sg.InputText()],
              [sg.Text('Введите название папки YandexДиска')],
              [sg.InputText()],
              [sg.Button('Ввести'), sg.Button('Отмена')]]

    window = sg.Window('VK2YaDisk', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Отмена':
            break
        if event == 'Ввести':
            vk_user_id = values[0]
            ya_disk_token = values[1]
            vk_token = values[2]
            ya_disk_path = values[3]
            break
    return vk_user_id, ya_disk_token, vk_token, ya_disk_path


# Popup успешной загрузки
def success_popup():
    layout = [[sg.Text('Фото успешно загружены на Yandex.Диск!')],
              [sg.Button('OK')]
              ]
    window = sg.Window('Успех', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'OK':
            break


# Popup ошибки загрузки
def error_popup():
    layout = [[sg.Text('Ошибка при загрузке фотографий!')],
              [sg.Button('Отмена')]
              ]
    window = sg.Window('Ошибка', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Отмена':
            break


init_input()
new_upload = DownloadFromVk(vk_user_id, vk_token, ya_disk_token)
new_upload.create_folder()
new_upload.upload_photos(new_upload.user_id)

