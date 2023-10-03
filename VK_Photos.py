import requests
from pprint import pprint
import time  # Для перевода unix даты в читаемый формат
from urllib.parse import urlencode
from tqdm import tqdm
import json


def oauth_user():  # Авторизация пользователя
    base_url = 'https://oauth.vk.com/authorize'
    app_id = 51754857
    params = {'client_id': app_id, 'redirect_uri': 'https://oauth.vk.com/blank.html', 'display': 'page',
              'scope': 'photos', 'response_type': 'token'}
    oauth_url = f'{base_url}?{urlencode(params)}'
    return oauth_url


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version, 'album_id': 'profile', 'extended': 1,
                       'photo_sizes': 1}
        self.base_url = 'https://oauth.vk.com/authorize'

    def users_photos(self):  # Получем информацию о фотографиях
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        photos_dict = response.json()
        return photos_dict


class YA:
    def __init__(self, photos_dict):
        self.ya_token = input(
            'Введите токен Яндекс Полигона: ')
        self.photos_dict = photos_dict
        self.params = {'path': input('Введите имя новой папки: ')}

    def ya_photos(self):  # Создаем папку на Яндекс диске
        ya_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        token = self.ya_token
        headers = {'Authorization': token}
        params = self.params
        response = requests.put(ya_url, headers=headers, params=params)
        st_code = response.status_code
        if st_code != 201:  # Проверка существующей папки
            print(f'По указанному пути уже существует папка {params["path"]}. Попробуйте еще раз')
            ya.ya_photos()
        else:
            print(f'Создана папка {params["path"]}')
        return response.json()

    def count_photos(self):  # Получаем общее количество фотографий
        all_photos = self.photos_dict['response']['count']
        print(f'Фотографий Вашего профиля: {all_photos}')
        post_photo = 5 if all_photos > 5 else all_photos
        get_up_photo = int(input(f'Сколько фотографий Вы хотите скопировать (по умолчанию {post_photo})?: '))
        if get_up_photo > all_photos or get_up_photo <= 0:
            get_up_photo = post_photo
            return get_up_photo
        else:
            return get_up_photo

    def ya_upload_photo(self, get_up_photo):
        url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'  # url для запроса загрузки файла
        token = self.ya_token
        headers = {'Authorization': token}
        file_name_dict = {}
        get_up_photo = get_up_photo
        data = []
        for i in range(get_up_photo):
            photo = self.photos_dict['response']['items'][i]
            file_name = f"{photo['likes']['count']}"  # Создаем имя файла по количеству лайков
            photo_size = photo['sizes'][-1]['type']
            photo_link = photo['sizes'][-1]['url']
            if file_name in file_name_dict:
                date_gm = time.gmtime(photo['date'])  # Перевод даты
                date = time.strftime("_%B_%d_%Y", date_gm)
                file_name += date
                file_name_dict[file_name] = photo_link
                data.append({'file_name': f"{file_name}.jpg", 'size': photo_size})
            else:
                file_name_dict[file_name] = photo_link
                data.append({'file_name': f"{file_name}.jpg", 'size': photo_size})

        for key, value in tqdm(file_name_dict.items()):
            time.sleep(0.1)
            params = {'url': value, 'path': f"{self.params['path']}/{key}.jpg"}
            response = requests.post(url_upload, headers=headers, params=params)
        return data

    def data_json(self, data):
        data = data
        with open('photo.json', 'w') as file:
            json.dump(data, file, indent=2)
            return


vk_oauth = oauth_user()  # Авторизовываем пользователя и передаем ему ссылку для получения токена и id
pprint(vk_oauth)
access_vk_token = input('Введите access_token: ')
user_vk_id = input('Введите user_id: ')

vk = VK(access_vk_token, user_vk_id)
vk_photos_dict = vk.users_photos()  # Словарь фотографий

ya = YA(vk_photos_dict)
ya_path = ya.ya_photos()  # Создаем папку на ЯДиске

all_count_photos = ya.count_photos()

data_p = ya.ya_upload_photo(all_count_photos)

data_json = ya.data_json(data_p)
