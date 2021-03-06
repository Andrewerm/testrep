from services.common import providerAPI

class AvitoApi(providerAPI):
    BASE_URL='https://api.avito.ru'
    REQURL='/core/v1'
    AUTORIZATION_URL='/token'

    def info_adv(self, item_id):
        if not self.check_time_session_valid():
            self.get_token()
        url=self.BASE_URL+self.REQURL+'/accounts/'+self.auth_params['user_id']+'/items/'+item_id
        return self.resp("GET", url,headers=self.bearer )
