from django import forms
from .models import Brands, Stores, Catalog
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .servicesCRM import DEPARTURE_CITIES


class BrandForm(forms.ModelForm):
    class Meta:
        model=Brands
        fields=['name', 'description', 'slug']

class SupplierForm(forms.Form):
    name=forms.CharField(max_length=20)
    slug=forms.SlugField()

class StoresForm(forms.ModelForm):
    class Meta:
        model=Stores
        fields=['catalog_item', 'quantity', 'wholesale_price', 'supplier']

class CatalogForm(forms.ModelForm):
    class Meta:
        model=Catalog
        fields=['article', 'brand_name', 'model_name', 'model_series']

class LoginForm(forms.Form):
    username=forms.CharField(max_length=11, widget=forms.TextInput(attrs={'autofocus':True}))
    password=forms.CharField(widget=forms.PasswordInput)


class UserRegForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','first_name', 'last_name', 'email']


class OrderInfoForm(forms.Form):
    recieverFIO=forms.CharField(label='ФИО получателя', max_length=50)
    selectPVZ=forms.ChoiceField(label='ПВЗ СДЭК получателя')
    choices=list(map(lambda item: (item['id'], item['name']),DEPARTURE_CITIES))
    selectShippingFrom=forms.ChoiceField(label='Город отправки', widget=forms.RadioSelect,
                                         choices=choices, initial=(DEPARTURE_CITIES[0]['id'],DEPARTURE_CITIES[0]['name']))
    fromSaratov=forms.ChoiceField(label='Тариф СДЭК из Саратова')
    fromKazan = forms.ChoiceField(label='Тариф СДЭК из Казани')
    fromChelny = forms.ChoiceField(label='Тариф СДЭК из Н. Челнов')
    insurance=forms.IntegerField(label='Страховка груза (руб.)', required=False)

class OrderInfoFormNonPVZ(OrderInfoForm):
    selectPVZ=forms.ChoiceField(label='ПВЗ СДЭК получателя', required=False, widget=forms.Select(attrs={'disabled':'disabled'}))

class DashBoardForm(forms.Form):
    checkBoxOrders=forms.BooleanField(label='Импортировать заказы',
                                      required=False,
                                      widget=forms.CheckboxInput(attrs={'onclick':"id_depthDaysOrders.disabled=!this.checked"}))
    depthDaysOrders=forms.IntegerField(label='Глубина импорта заказов (дней)', required=False)
    checkBoxProducts=forms.BooleanField(label='Импортировать товары',
                                        required=False,
                                        widget=forms.CheckboxInput(attrs={'onclick':"id_depthDaysProducts.disabled=!this.checked"}))
    depthDaysProducts=forms.IntegerField(label='Глубина импорта товаров (дней)',
                                         widget=forms.NumberInput(attrs={'disabled':'disabled'}), required=False)
    checkBoxGroups=forms.BooleanField(label='Импортировать группы', required=False)


# форма для загрузки файлов
class UploadFileForm(forms.Form):
    file = forms.FileField()