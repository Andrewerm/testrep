from crmApp.models import AliProducts, Catalog, Stores, Suppliers,Brands, AliFeedOperations, AliFeedOperationsLog
from crmApp.servicesCRM import serviceAli, check_funcs
import re, json
from services.google_services import importMyStockVostok, importMyStockMoskvin, importTradeChas
from services.avangard import AvangardApi, AvangardImportProducts
import csv
from io import StringIO




def updatingData(**kwargs):
    brand=kwargs['brand']
    article=kwargs['article']
    model_name=kwargs.get('model_name') or article
    idProduct=kwargs.get('idProduct') or ''
    avangardsession=kwargs.get('avangardsession')
    supplier=kwargs['supplier']
    quantity, price=kwargs.get('quantityprice') or avangardsession.get_stock(idProduct) # получаем данные из API Авангард
    item = Catalog.objects.filter(brand_name=brand, article=article)  # ищем модель в Каталоге
    # quantity, price=
    try:
        if item.exists():
            Stores.objects.update_or_create(catalog_item=item.first(),supplier=supplier, defaults={
                                                                                 'quantity': quantity,
                                                                                 'innerID':idProduct,
                                                                                 'wholesale_price':price})
            print(f'На склад {supplier} добавили {brand.name} {article}')
        else:
            newitem = Catalog.objects.create(article=article, brand_name=brand, model_name=model_name)
            print(f'в Каталог и на склад {supplier} добавили {brand.name} {article}, ')
            Stores.objects.create(catalog_item=newitem, quantity=quantity, supplier=supplier, innerID=idProduct,wholesale_price=price)
    except Exception as err:
        print(err)


def VostokParsing(data): # парсинг файла
    brandVostok=Brands.objects.get(name='Восток')
    s=AvangardApi()
    supplier = Suppliers.objects.get(name='Авангард')
    for data_item in data:
        article=re.search('\d{6}', data_item[1])[0]
        if re.search('ремень', data_item[1]):
            article+='r'
        elif re.search('браслет', data_item[1]):
            article+='b'
        try:
            updatingData(brand=brandVostok, article=article, model_name=article[:-1],
                         supplier=supplier, idProduct=data_item[2],avangardsession=s)
        except Exception as err:
            print(err)
    s.cart_cleaning()

def MoskvinParsing(data):
    brandMoskvin=Brands.objects.get(name='Mikhail Moskvin')
    s=AvangardApi()
    supplier=Suppliers.objects.get(name='Авангард')
    for data_item in data:
        parts=data_item[1].split(' ')
        article=parts[2]
        updatingData(brand=brandMoskvin, article=article,  supplier=supplier, idProduct=data_item[2],avangardsession=s)
    s.cart_cleaning()


def GepardParsing(data):
    brandGepard=Brands.objects.get(name='Gepard')
    s=AvangardApi()
    supplier = Suppliers.objects.get(name='Авангард')
    for data_item in data:
        parts=data_item[1].split(' ')
        article=parts[1]
        updatingData(brand=brandGepard , article=article, supplier=supplier, idProduct=data_item[2],avangardsession=s)
    s.cart_cleaning()

def SlavaParsing(data):
    brandGepard = Brands.objects.get(name='Слава')
    s = AvangardApi()
    supplier = Suppliers.objects.get(name='Авангард')
    for data_item in data:
        parts = data_item[1].split(' ')
        article = parts[1].replace('-','/',1)
        updatingData(brand=brandGepard, article=article, supplier=supplier, idProduct=data_item[2], avangardsession=s)
    s.cart_cleaning()

def DkleinParsing(data):
    brandGepard = Brands.objects.get(name='Daniel Klein')
    s = AvangardApi()
    supplier = Suppliers.objects.get(name='Авангард')
    for data_item in data:
        parts = data_item[1].split(' ')
        article = parts[-1]
        updatingData(brand=brandGepard, article=article, supplier=supplier, idProduct=data_item[2], avangardsession=s)
    s.cart_cleaning()

# def handle_avangard_file(file):
#     BRANDS={'vostok':VostokParsing,
#             'mikhail_moskvin': MoskvinParsing,
#             'gepard_mikhail_moskvin': GepardParsing,
#             'slava':SlavaParsing,
#             'daniel_klein': DkleinParsing
#             }
#     file_data=file.read().decode('utf-8') # получаем содержимое файла
#     file_data=file_data[1:-1] # удаляем первую и последнюю мешающую кавычку
#     lines=file_data.split('"\r\n') # разбиваем на строки
#     data=list(map(lambda x: x[1:].split('";"'), lines)) # строки разбиваем на поля
#     # обнуляем склад Авангард
#     Stores.objects.filter(supplier=Suppliers.objects.get(name='Авангард')).update(quantity=0)
#     # фильтруем нужны бренд
#     for (brand, func) in BRANDS.items():
#         filt=list(filter(lambda x:x[0]==brand, data))
#     # парсингуем и загружаем в базу
#         if len(filt)>0:
#             func(filt)


def handle_myownstore():
    print('импортируем остатки из своего склада')
    dataVostok=importMyStockVostok.handled_data()
    brand = Brands.objects.get(name='Восток')
    supplier = Suppliers.objects.get(name='Мой склад')
    Stores.objects.filter(supplier=supplier).update(quantity=0)
    for data_item in dataVostok:
        updatingData(brand=brand , article=data_item[1], model_name=data_item[1][:-1],
                     supplier=supplier, quantityprice=(data_item[2], data_item[3]), idProduct=data_item[4] )
    dataMoskvin=importMyStockMoskvin.handled_data()
    MOSKVIN='Mikhail Moskvin'
    GEPARD='Gepard Moskvin'
    brandMoskvin = Brands.objects.get(name=MOSKVIN)
    brandGepard = Brands.objects.get(name='Gepard')
    for data_item in dataMoskvin:
        if data_item[0]==MOSKVIN:
            brand=brandMoskvin
        elif data_item[0]==GEPARD:
            brand=brandGepard
        else:
            raise Exception
        updatingData(brand=brand , article=data_item[1],
                     supplier=supplier, quantityprice=(data_item[2], data_item[3]))


def handle_tradechas():
    print('импортируем остатки из Трейдчас')
    dataVostok=importTradeChas.handled_data()
    # brand = Brands.objects.get(name=dataVostok[0])
    supplier = Suppliers.objects.get(name='Трейдчас')
    Stores.objects.filter(supplier=supplier).update(quantity=0)
    for data_item in dataVostok:
         updatingData(brand=Brands.objects.get(name=data_item[0]) , article=data_item[1], model_name=data_item[1][:-1],
                      supplier=supplier, quantityprice=(data_item[2],0))




@check_funcs
def handle_syncInventory():
    listing=AliProducts.objects.all() #[476:478] # пробег по всем продуктам Aliexpress
    print(f'начинаем синхронизацию остатков с Али кол-во: {listing.count()}')
    requemas=[]
    for counter, spu  in enumerate(listing):
        item={"aliexpress_product_id": spu.product_id,  "multiple_sku_update_list": []}
        for sku in spu.product.all():
            ind = next((i for i,x in enumerate(sku.SKU) if x=='r' or x=='b'), None) # пытаемся найти "r" или "b" в SKU
            model=sku.model+sku.SKU[ind] if ind else sku.model # прибавляем к модели "r" или "b"
            searchingModel=Catalog.objects.filter(article=model) if ind else Catalog.objects.filter(model_name=model)
            stock=sum([x.stock() for x in searchingModel],0)
            if stock:
                print(f'{counter+1} нашли {searchingModel.first().brand_name.name} {model} кол-во: {stock}')
            else:
                print(f'{counter+1}  {model} не нашли ')
            item["multiple_sku_update_list"].append({"sku_code": sku.SKU, "inventory": stock})
        if spu.product.count():
            requemas.append({"item_content_id":str(counter), "item_content":item})
    a = serviceAli()
    result=a.updateStockAmountAsync(json.dumps(requemas))
    jobid=result['aliexpress_solution_feed_submit_response']['job_id']
    request_id=result['aliexpress_solution_feed_submit_response']['request_id']
    AliFeedOperations.objects.create(jobID=jobid, request_id=request_id)

@check_funcs
def handle_getsyncInventoryResults(jobid):
    a=serviceAli()
    result=a.updateStockAmountAsyncResults(jobid)
    mas=[]
    for i in result['aliexpress_solution_feed_query_response']['result_list']['single_item_response_dto']:
        jobidmodel=AliFeedOperations.objects.get(jobID=jobid)
        data=AliFeedOperationsLog(job=jobidmodel, item_content_id= i['item_content_id'],
                                  item_execution_result=i['item_execution_result'])
        mas.append(data)
    AliFeedOperationsLog.objects.bulk_create(mas)
    pass



@check_funcs
def handle_AvangardProducts():

    BRANDS={'naruchnie_chasi/vostok':VostokParsing,
            'naruchnie_chasi/mikhail_moskvin': MoskvinParsing,
            'naruchnie_chasi/gepard_mikhail_moskvin': GepardParsing,
            'naruchnie_chasi/slava/slava_kvartsevie':SlavaParsing,
            'naruchnie_chasi/slava/slava_mekhanicheskie': SlavaParsing,
            'naruchnie_chasi/daniel_klein': DkleinParsing
            }
    # Определяем формат CSV от Авангард
    class Avangard_dialect(csv.Dialect):
        delimiter = ';'
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = '\n'
        quoting = csv.QUOTE_ALL
    adialect=Avangard_dialect()
    csv.register_dialect('avangard_dialect', adialect)
    # закончили с определением формата
    a=AvangardImportProducts()
    res=a.get_stock()
    buff = StringIO(res)
    reader_object = csv.DictReader(buff, dialect='avangard_dialect')
    mas=[]
    item= next(reader_object, None)
    while item:
        if item['folder_alias'] in BRANDS.keys():
            mas.append([item['folder_alias'], item['name'], item['code']])
        item = next(reader_object, None)
    # обнуляем склад Авангард
    Stores.objects.filter(supplier=Suppliers.objects.get(name='Авангард')).update(quantity=0)
    # # фильтруем нужны бренд
    for (brand, func) in BRANDS.items():
        filt=list(filter(lambda x:x[0]==brand, mas))
    # парсингуем и загружаем в базу
        if len(filt)>0:
            func(filt)

