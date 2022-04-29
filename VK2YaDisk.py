import requests
import json
import PySimpleGUI as sg
from tqdm import tqdm
import configparser
import time

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

    def get_photos_method(self, user_id):
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
        for file in tqdm(profile_list['response']['items']):
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

        with open('logs/log.json', 'a') as file:
            json.dump(logs_list, file, indent=2)

        if 500 > status != 400:
            print('Фотографии успешно загружены!')
        else:
            print('Ошибка при загрузке фотографий')

    def create_folder(self):
        params = {'path': self.file_path}
        headers = {'Content-Type': 'application/json',
                   'Authorization': self.yadisk}
        requests.api.put(self.mkdir_url, headers=headers, params=params)


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



init_input()
new_upload = DownloadFromVk(vk_user_id, vk_token, ya_disk_token)
new_upload.create_folder()
save_photos = new_upload.get_photos_method(new_upload.user_id)

