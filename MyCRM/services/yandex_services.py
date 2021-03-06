from services.common import providerAPI, check_funcs


yandexApiKey='ae46126c-27e7-419c-a44c-c503864debe8'

class Geocoder(providerAPI):
    BASE_URL='https://geocode-maps.yandex.ru/1.x/'

    def __init__(self, **kwargs):
        super().__init__()
        self.session_params['geocode']=kwargs['address']

    def get_token(self):
        self.session_params={'apikey':yandexApiKey, 'format':'json'}

    @property
    @check_funcs
    def get_coords_by_address(self):
        s='&'.join([f'{i}={self.session_params[i]}'  for i in self.session_params])
        res=self.resp('GET', f'{self.BASE_URL}?{s}')
        self.precision=res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['precision']
        self.kind=res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['kind']
        res2 = res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        self.coord={'latitude':res2[1], 'longitude':res2[0]}
        return self.coord


