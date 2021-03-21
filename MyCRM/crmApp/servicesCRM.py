from services.ali_services import AliApi
from services.cdek_services import CdekAPI, Calc_tarif
from services.pochta_services import PochtaApi
from services.yandex_services import Geocoder
from abc import ABC, abstractmethod
from .models import AliProducts, AliOrders, AliOrdersProductList,\
    AliGroupList, AliChildGroupList, AliOrdersDetailedInformation, ProductsSKU
from django.db.models.query import QuerySet
from datetime import datetime, timedelta
from djmoney.money import Money
import re

# ключи Али
appAliKey='31102380'
Alisecret='ea36c75363323184e6779cff827368d4'
AlisSessionKey='50000000b46gvlSAoYNrD9bGtGosBVRl9gEyhqRvenhMpaltVZEzoLTORH13ec5298w'

# сдэк
Account='0372b3fff5d6707cd1633469403952df'
Secure_password='afc14015cce5555ce582bf97b963d2d2'

# ключи Почты РФ
tokenPochta='IomDCsxKO_jjc3yx7eocmSZ3FYDIMMGn'
loginPochta='andrewerm@yandex.ru'
secretPochta='531930Ab-'

CountItemsInIteration=100 # кол-во элементов в каждом запрос к Али
SizeSlice=30 # размер среза (кол-во записей в партии) при пакетной загрузке данных

NOPVZ=[{'code':'000', 'location':{'address': 'Нет ПВЗ' }}]
DEPARTURE_CITIES=[{'id':'fromKazan','name': 'Чистополь','PVZ':'CHSP1', 'index':'422980'},
                  {'id':'fromChelny','name':'Набережные Челны','PVZ':'NCHL6', 'index':'423802'}]

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

# декоратор - если возвращаемое значение строка и похожа на объект JSON, то преобразуем в dict
def eval_handler(func):
    def wrapper(*args, **kwargs):
        return_value = func(*args, **kwargs)
        if type(return_value) is str and return_value and (return_value[0] == '{' or return_value[0] == '['):
                  return eval(return_value)
        else:
            return return_value
    return wrapper


def aliStrToDate(dict, strTime, delta):
        for i in strTime:
            t=dict.get(i)
            if t:
                dt=datetime.strptime(f'{t} {delta}', '%Y-%m-%d %H:%M:%S %z')
                dict[i]=dt
        return dict

def simpleMoneyToMoneyField(dict, simpleMoney):
        for i in simpleMoney:
            s=dict.get(i)
            if s:
                dict[i]=Money(float(s['amount']), s['currency_code'])
        return dict

class AliDataIterations(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __load_data__(self):
        pass

    def __delta_time__(self, depthUpdatingDays, delta):
        u = datetime.utcnow()
        delta = timedelta(days=depthUpdatingDays, hours=delta) # снимаем разницу во времени с UTC
        return u-delta

    def __len__(self):
        return self.total_count

    def __init__(self, methodAli, depthUpdatingDays=None):
        self.method=methodAli
        self.current_page = 1
        self.current_item=-1
        self.depthUpdatingDays=depthUpdatingDays
        self.__load_data__(1, CountItemsInIteration)

    def __next__(self):
        if not self.total_count:
            raise StopIteration
        while self.current_page <= self.total_page:
            while self.current_item < self.page_size - 1:
                self.current_item += 1
                return self.data[self.current_item]
            self.current_page += 1
            if self.current_page > self.total_page:
                raise StopIteration
            self.__load_data__(self.current_page, CountItemsInIteration)
            self.current_item = -1


class iterOrderList(AliDataIterations):

    def __load_data__(self, page, count):
        res = self.method(page, count, self.__delta_time__(self.depthUpdatingDays, 7))
        self.total_count = res['aliexpress_solution_order_get_response']['result']['total_count']
        self.total_page = res['aliexpress_solution_order_get_response']['result']['total_page']
        if self.total_count:
            self.data=res['aliexpress_solution_order_get_response']['result']['target_list']['order_dto']
            self.page_size = len(self.data)

@check_funcs
class iterProductList(AliDataIterations):
    def __load_data__(self, page, count):
        res = self.method(page, count, self.__delta_time__(self.depthUpdatingDays, -8))
        self.total_count = res['aliexpress_solution_product_list_get_response']['result']['product_count']
        self.total_page = res['aliexpress_solution_product_list_get_response']['result']['total_page']
        if self.total_count:
            self.data=res['aliexpress_solution_product_list_get_response']['result']['aeop_a_e_product_display_d_t_o_list']['item_display_dto']
            self.page_size = len(self.data)

class iterGroupList(AliDataIterations):
    def __load_data__(self, page, count):
        res=self.method()
        self.total_count=1
        self.total_page=1
        self.data = res['aliexpress_product_productgroups_get_response']['result']['target_list']['aeop_ae_product_tree_group']
        self.page_size = len(self.data)

class orderAliInfo():

    # обновление данных из таблицы кастомных данных
    def __getAliDetailInfoOrder__(self):
            result=self.aliAPIsession.aliOrderInfo(self.order_id)['aliexpress_solution_order_info_get_response']['result']['data']
            inBD={item:result[item] for item in result if item in self.__fieldsAliOrdersDetailedInformations__}
            t=('gmt_modified', 'gmt_create', 'gmt_trade_end')
            result2 = aliStrToDate(inBD,t, '-0700')
            return result2

    # нормализация адреса сервисом Почты РФ
    def __normalised_adress__(self):
        a = PochtaApi(client_id=loginPochta, client_secret=secretPochta, token=tokenPochta)
        addres_from_ali=self.alidetailinfo_receipt_address
        m=['zip', 'country', 'province', 'city', 'detail_address', 'address2' ]
        addr = ','.join(list(map(lambda x: addres_from_ali.get(x,''),m)))
        pochtaaddr=a.normAddress(addr)
        if pochtaaddr['quality-code']=='GOOD':
            m=['index', 'region', 'area','place',  'street', 'house', 'room']
            full_normalized_address = ','.join(list(map(lambda x: pochtaaddr.get(x,''),m)))
        else:
            full_normalized_address=pochtaaddr['original-address']
        return {'normalized_address':pochtaaddr, 'full_normalized_address':full_normalized_address}

    def __coords__(self):
        a = Geocoder(address=self.pochta_full_normalized_address)
        return {'coord':a.get_coords_by_address}


    def __cdek_pvz__(self):
        def calc_dist(inp): # расчёт дистанции от адреса получателя до СДЭК
            ax=float(self.ya_coord['longitude'])
            bx=float(inp['location']['longitude'])
            ay=float(self.ya_coord['latitude'])
            by=float(inp['location']['latitude'])
            return ((ax-bx)**2+(ay-by)**2)**(1/2)
        a=CdekAPI(client_id=Account, client_secret=Secure_password)
        listOfPVZ=a.GET_PVZ(postal_code=self.pochta_normalized_address['index'])
        if listOfPVZ:
            listOfPVZ.sort(key=calc_dist)  # сортируем по дистанции до адреса получателя
            return {'pvz': listOfPVZ, 'isPVZ': 1}  # если есть ПВЗ, то возвращаем признак 1
        else:
            return {'pvz': NOPVZ, 'isPVZ': 2}
        # если возвращется 0 ПВЗ, то возвращаем признак 2


    def __cdek_order_status__(self):
        a=CdekAPI(client_id=Account, client_secret=Secure_password)
        uuid=self.cdekorderresponse_cdekResponse
        res=a.get_order_info(uuid=uuid['entity']['uuid'])
        return {'cdekStatus':res}


    def __cdek_order_response__(self):
        return getattr(AliOrdersDetailedInformation.objects.get(order=self.order_id),'cdekResponse')

    def __cdektarifes__(self):
        a=Calc_tarif()
        res={i['id']: a.get_tarif(from_post_code=i['index'],
                                              to_post_code=self.pochta_normalized_address['index']) for i in DEPARTURE_CITIES}
        return {'tarifes':res}

    def __aliorders__(self):
        a = AliOrders.objects.get(order_id=self.order_id)
        return a

    def __aliordersproductlist__(self):
        a = AliOrdersProductList.objects.filter(main_order=self.order_id)
        return a

    def cdek_response_save(self, response):
        a=AliOrdersDetailedInformation.objects.get(order=self.order_id)
        a.cdekResponse=response
        a.save(update_fields=['cdekResponse'])


    def __init__(self, order_id):
        self.order_id=order_id
        self.aliAPIsession = AliApi(app_key=appAliKey, secret=Alisecret, sessionkey=AlisSessionKey)
        self.__fieldsAliOrders__=[i.name for i in AliOrders._meta.get_fields()]
        self.__fieldsAliOrdersDetailedInformations__ = [i.name for i in AliOrdersDetailedInformation._meta.get_fields()]
        self.__fieldsAliOrdersProductList__ = [i.name for i in AliOrdersProductList._meta.get_fields()]
        self.__allFields__=[*self.__fieldsAliOrders__, *self.__fieldsAliOrdersDetailedInformations__, *self.__fieldsAliOrdersProductList__ ]

    @eval_handler
    def __getattr__(self, item):
        SERVICES = {'alidetailinfo': self.__getAliDetailInfoOrder__, 'pochta': self.__normalised_adress__,
                    'ya': self.__coords__, 'cdek':self.__cdek_pvz__,
                    'cdektarif':self.__cdektarifes__, 'aliorders':self.__aliorders__,
                    'aliordersproductlist': self.__aliordersproductlist__,
                    'cdekorderresponse':self.__cdek_order_response__,
                    'cdekorderstatus': self.__cdek_order_status__}
        service, *rest=item.split('_') # service - имя сервиса в аттрибуте
        attr='_'.join(rest) # attr - сам аттрибут
        print(f' сервис: {service}, аттрибут: {attr}')

        if service not in SERVICES or attr not in self.__allFields__: # если нет такого маршрута
             raise AttributeError(f'такого сервиса {service} с аттрибутом {attr} нет')
        # ищем аттрибут в базе, если там пустая строка, то запрашшиваем в API и записываем в базу
        if service in ('alidetailinfo', 'pochta', 'ya', 'cdek', 'cdektarif','cdekorderresponse','cdekorderstatus'):
            return getattr(AliOrdersDetailedInformation.objects.get_or_create(order_id=self.order_id)[0], attr)\
            or getattr(AliOrdersDetailedInformation.objects.update_or_create(order=self.order_id, defaults=SERVICES[service]())[0],attr)
        if service in ('aliorders', 'aliordersproductlist'):
            res=SERVICES[service]()
            if isinstance(res, QuerySet):
                return [getattr(i,attr) for i in res]
            else:
                return getattr(res, attr)

    def product_list_for_cdek(self, insurance):
        products=self.__aliordersproductlist__()
        weight=int(100/products.count())
        cost=int(int(insurance)/products.count())
        res=[{'name': 'Часы Восток', 'ware_key': re.search('\d{6}', item.product_name)[0],
              'payment': {'value': 0},'cost': cost, 'weight': weight, 'amount': 1} for item in products]
        # res=[{'name': 'Часы Восток', 'ware_key': '123456',
        #       'payment': {'value': 0},'cost': cost, 'weight': weight, 'amount': 1} for item in products]

        return [{'number': '001', 'weight': 100, 'items': res }]



class serviceAli():
    def __init__(self):
        self.session = AliApi(app_key=appAliKey, secret=Alisecret, sessionkey=AlisSessionKey)

    @check_funcs
    def updateOrderList(self, depthUpdatingDays):
        a=iterOrderList(self.session.aliOrderList, depthUpdatingDays=depthUpdatingDays)
        print(len(a))
        j=0
        for i in a:
            j+=1
            print(j, ' ' , i)
            t=('gmt_update', 'gmt_send_goods_time', 'gmt_pay_time','gmt_create')
            m=('pay_amount', 'loan_amount', 'escrow_fee')
            i = aliStrToDate(i,t, '-0700')
            i=simpleMoneyToMoneyField(i,m)
            productlist=i.pop('product_list')
            AliOrders.objects.update_or_create(order_id=i['order_id'], defaults=i)
            self.__importProductsInOrderList__(productlist['order_product_dto'], i['order_id'])

    def __importProductsInOrderList__(self, data, main_order_id):
        for i in data:
            t=('send_goods_time',)
            m=('total_product_amount', 'product_unit_price', 'logistics_amount')
            i = aliStrToDate(i,t, '+0800')
            i = simpleMoneyToMoneyField(i,m)
            productID=i['product_id']
            i['product']=AliProducts.objects.get(product_id=productID)
            i['main_order']=AliOrders.objects.get(order_id=main_order_id)
            AliOrdersProductList.objects.update_or_create(order_id=i['order_id'], defaults=i)

    def updateProducts(self, depthUpdatingDays): # импорт товаров из Али
        a=iterProductList(self.session.aliProductList, depthUpdatingDays=depthUpdatingDays)
        j=0
        for i in a:
            j+=1
            print(j, ' ' , i)
            i = aliStrToDate(i,('gmt_create','gmt_modified'),'+0800')
            item=AliProducts.objects.update_or_create(product_id=i['product_id'], defaults=i)[0]
            # добавляем SKU
            productInfo = self.getProduct(i['product_id'])  # получаем инфу из API Али
            try:
                # получаем список SKU по продукту
                skulist = productInfo['aeop_ae_product_s_k_us']['global_aeop_ae_product_sku']
                # получаем все аттрибуты карточки модели
                attrs=productInfo['aeop_ae_product_propertys']['global_aeop_ae_product_property']
                # ищем в аттрибутах бренд и модель и русское наименование
                brand=next(x for x in attrs if x['attr_name_id']==2)['attr_value']
                model=next(x for x in attrs if x['attr_name_id']==3)['attr_value']
                subjectlist=productInfo['multi_language_subject_list']['global_subject']
                subject=next(x for x in subjectlist if x['locale']=='ru_RU')['subject']
                for sku in skulist:
                        scucode = sku.get('sku_code', i['product_id'])
                        ProductsSKU.objects.update_or_create(SKU=scucode, SPU=item, defaults={'brand':brand,
                                                             'model': model, 'subject':subject})
                        print(f'... добавили SKU {scucode} модели {brand} {model}')
                if len(skulist)==0:
                     raise StopIteration
            except KeyError as err:
                print(f'ошибка {err}')
            except StopIteration as err:
                print(f'не нашёлся аттрибут в {i["product_id"]},  ошибка {err}')



    def getProduct(self, id):
        res=self.session.aliProductInfo(id)
        try:
            res2=res['aliexpress_solution_product_info_get_response']['result']
            return res2
        except KeyError as keyerr:
            print(f'ошибка парсинга ответа Ali {keyerr}')



    def __getAliDetailInfoOrder__(self,id):
            FIELDS={'buyer_info', 'gmt_modified', 'receipt_address', 'gmt_trade_end', 'buyerloginid', 'order_status'}
            result=self.session.aliOrderInfo(id)['aliexpress_solution_order_info_get_response']['result']['data']
            inBD={item:result[item] for item in result if item in FIELDS}
            return inBD

    def __updateChildGroupList__(self, data, group_id):
        for i in data:
            i['ali_group']=AliGroupList.objects.get(group_id=group_id)
            AliChildGroupList.objects.update_or_create(group_id=i['group_id'], defaults=i)

    def updateGroupList(self):
        a=iterGroupList(self.session.aliGetGroupList)
        for i in a:
            print(i)
            if i.get('child_group_list'):
                child_group_list = i.pop('child_group_list')
                i['hasChild']=True
                AliGroupList.objects.update_or_create(group_id=i['group_id'], defaults=i)
                self.__updateChildGroupList__(child_group_list['aeop_ae_product_child_group'], i['group_id'])
            else:
                AliGroupList.objects.update_or_create(group_id=i['group_id'], defaults=i)

    def updateStockAmountSync(self,id,amount):
        # req=[{"item_content_id": "A00000000Y1",
        #       "item_content": {
        #           "aliexpress_product_id": id,
        #      ]


        a=self.session.aliSolutionFeed('PRODUCT_STOCKS_UPDATE', 'test')


    def updateStockAmountAsync(self,batch):
        result = self.session.aliSolutionFeed('PRODUCT_STOCKS_UPDATE', batch)
        print(result)
        return result

    def updateStockAmountAsyncResults(self, jobid):
        result = self.session.aliSolutionResponse(jobid)
        print(result)
        return result




