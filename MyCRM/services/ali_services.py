from services.common import providerAPI
import hmac , pytz
from datetime import datetime
import copy
AttemptCount=5 # кол-во попыток соединения с API Ali

class AliApi(providerAPI):
    BASE_URL ='https://eco.taobao.com/router/rest'
    METHOD=None

    def __aop_signature(self, appsecret, kwargs):
        a = [(s, kwargs[s]) for s in kwargs] # словарь в список таплов
        a.sort() # сортировка
        result = "".join(["%s%s" % (s[0], s[1]) for s in a])
        signature = hmac.new(
            appsecret.encode("utf-8"),
            result.encode("utf-8"),
            'MD5'          # hmac_md5
        ).hexdigest()  # шестнадцатеричный
        return str(signature).upper()

    def __aop_timestamp(self):
        # временная метка по китайское временной зоне
        tz = pytz.timezone('Asia/Shanghai')
        timestamp = datetime.now(tz=tz).strftime('%Y-%m-%d %H:%M:%S')
        return timestamp

    def get_token(self):
        pass

    def __reqApi(self, **kwargs):
        url=self.BASE_URL
        payload = {'app_key':self.auth_params['app_key'],
                   'format':'json',
                   'method':self.METHOD,
                   'partner_id':'apidoc',
                   'sign_method':'hmac',
                   'v':'2.0',
                   'timestamp':self.__aop_timestamp(),
                   'session':self.auth_params['sessionkey']}
        if kwargs:
            payload[kwargs['key']]=kwargs['value']
            if kwargs.get('changes'):
                payload['item_list']=kwargs['changes']
        sign=self.__aop_signature(self.auth_params['secret'], payload)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload['sign']=sign
        i=copy.copy(AttemptCount)
        result='Ошибка сервера!' # заглушка
        while i>0 and (type(result)!=dict or result.get('error_response')): # проверяем ответ на безошибочность и кол-во итераций
            print(f'Conecting to API ...  {AttemptCount-i+1}')
            result=self.resp("POST", url, headers=headers, data=payload)
            i-=1
        return result

    def aliProductList(self, current_page,page_size, fromDateTime, status='*'):
        self.METHOD='aliexpress.solution.product.list.get'
        key='aeop_a_e_product_list_query'
        value="{'product_status_type':'"+status+"', page_size:"+str(page_size)+", gmt_modified_start: '"+fromDateTime.strftime('%Y-%m-%d %H:%M:%S')+"', current_page:"+str(current_page)+"}"
        return self.__reqApi(key=key, value=value)

    def aliProductInfo(self, product_id):
        self.METHOD='aliexpress.solution.product.info.get'
        key='product_id'
        value=product_id
        return self.__reqApi(key=key, value=value)

    def aliOrderList(self, current_page,page_size, fromDateTime, status='*' ):
        self.METHOD='aliexpress.solution.order.get'
        key='param0'
        value="{page_size:"+str(page_size)+", current_page:"+str(current_page)+", modified_date_start: '"+fromDateTime.strftime('%Y-%m-%d %H:%M:%S')+"', order_status: '"+status+"'}"
        return self.__reqApi(key=key, value=value)

    def aliOrderInfo(self, order_id):
        self.METHOD='aliexpress.solution.order.info.get'
        key='param1'
        value="{order_id: "+str(order_id)+"}"
        return self.__reqApi(key=key, value=value)

    def aliGetGroupList(self):
        self.METHOD='aliexpress.product.productgroups.get'
        return self.__reqApi()

    # метод асинхронного обновления данных
    def aliSolutionFeed(self, operationtype, changes):
        self.METHOD = 'aliexpress.solution.feed.submit'
        key = 'operation_type'
        value = operationtype
        return self.__reqApi(key=key, value=value, changes=changes)

    def aliSolutionResponse(self, jobid):
         self.METHOD = 'aliexpress.solution.feed.query'
         key = 'job_id'
         value = jobid
         return self.__reqApi(key=key, value=value)