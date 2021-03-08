from services.common import providerAPI
from crmApp.models import tokensApi, Stores
from django.db.models import F, Value
from datetime import datetime, timezone
import random
import pickle
LOGIN='andrewerm@yandex.ru'
PASSWORD='35803440'
BULK_SLICE=40

class AvangardImportProducts(providerAPI):
    BASE_URL = 'http://api.avangard-time.ru/products/'
    def get_token(self):
        pass

    def get_stock(self):
        params = {'login': LOGIN, 'password': PASSWORD}
        url=self.BASE_URL
        res=self.resp("POST", url, data=params, type='html')
        err=''
        i=0
        while not err and i<3:
            i+=1
            try:
                print('коннект к Авангард .... ')
                return res.text
            except Exception as err:
                    print(err)
        return ''





class AvangardApi(providerAPI):
    BASE_URL='https://avangard-time.ru/'
    AUTORIZATION_URL='profile/'
    def get_token(self):
        data, created=tokensApi.objects.get_or_create(nameApi='avangard')
        if created or not data.token or data.data_expires<datetime.now(timezone.utc):
            url=self.BASE_URL+self.AUTORIZATION_URL
            params = {'login': LOGIN, 'password': PASSWORD, 'action':'login', 'remember':'on', 'stoprobot':''}
            self.session.headers.update({
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
                })

            print('Получаем новый куки от сайта Авангард')
            self.resp("POST", url, data=params, type='html')
            sessionSerial=pickle.dumps(self.session)
            data.token=sessionSerial
            data_expires= next(x for x in self.session.cookies if x.name == 'hash').expires
            data.data_expires=datetime.fromtimestamp(data_expires, tz=timezone.utc)
            data.save()
        else:
            print('Используем старый куки от сайта Авангард')
            self.session=pickle.loads(data.token)


    def get_stock(self, id_avangard):
        rand=random.randint(100, 200)
        data = {'quantity':str(rand), 'ajax':'1', 'update':id_avangard }
        req=self.resp("POST", self.BASE_URL+'cart/', data=data)
        # data['quantity']=0
        # self.resp("POST", self.BASE_URL+'cart/', data=data)
        if req.get('excess'):
            stock=int(req['excess'])
            price=req.get('price')
            if price:
                price=float(price)
            else:
                price=0
            return (rand+stock,price)
        else:
            print(f'модели id {id_avangard} нету! ')
            return (0,0)


    def cart_cleaning(self):
        data={'cart_drop':'1'}
        self.resp("POST", self.BASE_URL + 'cart/', data=data, type='html')
        print('очистка корзины')



