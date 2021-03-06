from services.common import providerAPI
import base64, json

class PochtaApi(providerAPI):
    BASE_URL = 'https://otpravka-api.pochta.ru'
    NORM_ADR='/1.0/clean/address'

    def get_token(self):
        auth_keys=f'{self.auth_params["client_id"]}:{self.auth_params["client_secret"]}'
        auth_keysB=auth_keys.encode('UTF-8')
        userAuthB=base64.b64encode(auth_keysB)
        userAuth=userAuthB.decode('UTF-8')
        self.headers = {'X-User-Authorization': f'Basic {userAuth}',
                        'Authorization': f'AccessToken {self.auth_params["token"]}',
                        'Content-Type': 'application/json'
                        }
        print(userAuth)

    def normAddress(self, adress):
        url=self.BASE_URL+self.NORM_ADR
        d2=json.dumps([{'id':'adr 1', 'original-address':adress}])
        a=self.resp("POST", url, headers=self.headers, data=d2.encode('UTF-8'))
        return a[0]


