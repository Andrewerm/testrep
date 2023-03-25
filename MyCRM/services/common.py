import requests, time
from requests.exceptions import HTTPError
from abc import ABC
from crmApp.models import tokensApi
from datetime import datetime, timedelta, timezone

def check_funcs(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        print('начало выполнения '+func.__name__)
        return_value = func(*args, **kwargs)
        end = time.time()
        print(f'конец выполнения {func.__name__}, время выполнения: {round(end-start)} секунд.')
        return return_value
    return wrapper


class providerAPI(ABC):

    BASE_URL=None
    AUTORIZATION_URL=None
    REQURL=None

    def __init__(self, **kwargs):
        self.session=requests.Session()
        self.auth_params=kwargs
        self.get_token()

    def get_token(self):
        data, created=tokensApi.objects.get_or_create(nameApi='cdek')
        if created or not data.token or data.data_expires<datetime.now(timezone.utc):
            # если в БД ещё нет записи cdek или есть, но токена нет, или он просрочен
            url=self.BASE_URL+self.AUTORIZATION_URL
            params = {'grant_type': 'client_credentials', 'client_id': self.auth_params['client_id'],
              'client_secret': self.auth_params['client_secret']}
            self.session_params = self.resp("POST", url, data=params)
            data.token=self.session_params['access_token'].encode()
            delta = timedelta(seconds=int(self.session_params['expires_in']))
            data.data_expires=datetime.now(timezone.utc)+delta
            data.save()
            print('Получаем новый сессионный ключ от СДЭК')
        else:
            # если токен в БД есть и не просрочен
            print('Используем старый сессионный ключ от СДЭК')
            self.session_params={'access_token':data.token.decode()}
        self.bearer = {'Authorization': 'Bearer ' + self.session_params['access_token']}

    @check_funcs
    def resp(self, method, url, **kwargs):
        if kwargs.get('headers'):
            self.session.headers.update(kwargs['headers'])
        try:
            if method.upper()=='GET':
                response = self.session.get(url, timeout=30, params=kwargs.get('params'))
            elif method.upper()=='POST':
                response = self.session.post(url, timeout=40, data=kwargs.get('data'))
            else:
                return None
            print('url: '+url)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            # return {'errorOfResp':True}
        except Exception as err:
            print(f'Other error occurred: {err}')
            # return {'errorOfResp': True}
        else:
            try:
                if kwargs.get('type'):
                    if kwargs['type']=='html' or kwargs['type']=='text':
                        return response.text
                    if kwargs['type']=='content':
                        return response.content

                else:
                    return response.json()
            except Exception as err:
                   print(err)


