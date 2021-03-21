from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Brands, Catalog, Stores, Suppliers, AliOrdersProductList, AliProducts, AliOrders
from .forms import BrandForm, SupplierForm,\
    StoresForm, CatalogForm, LoginForm, UserRegForm, OrderInfoForm, OrderInfoFormNonPVZ, DashBoardForm, UploadFileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .servicesCRM import serviceAli, check_funcs, orderAliInfo, DEPARTURE_CITIES
from django.core.paginator import Paginator
from services.cdek_services import CdekAPI, CdekOrder
from services.utils import handle_myownstore, handle_tradechas, handle_syncInventory, handle_getsyncInventoryResults, handle_AvangardProducts



# # пункты отправления посылок
# SOURCE_CITIES = {'selectTarifSaratov':'SAR4', 'selectTarifKazan':'KZN37',
#                  'selectTarifChelny': 'NCHL6'}
# сдэк
Account='0372b3fff5d6707cd1633469403952df'
Secure_password='afc14015cce5555ce582bf97b963d2d2'

# Create your views here.
class BrandsView(ListView):
    pass
    # model = Brands
    # context_object_name = 'brands'
    # template_name = 'crmApp/brands/brands_list.html'

class BrandDelete(DeleteView):
    model = Brands
    context_object_name = 'brand'
    template_name = 'brands/brands_delete.html'
    success_url = reverse_lazy('crm:brand_list')

class CatalogView(ListView):
    model=Catalog
    context_object_name = 'catalog_items'
    template_name = 'catalogModels/catalog_models_list.html'

class BrandDetail(DetailView):
    model=Brands
    context_object_name = 'brand'
    template_name='brands/brand_detail.html'

class CatalogModelDetail(DetailView):
    model = Catalog
    context_object_name = 'item'
    template_name = 'catalogModels/catalog_model.html'

class StoresList(ListView):
    model=Stores
    context_object_name = 'store'
    template_name = 'stores/store_list.html'

def store_add(request):
    if request.method=='POST':
        form = StoresForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crm:store_list')
    else:
        form=StoresForm()
        return render(request, 'stores/store_add.html', context={'form': form})

def store_delete(request, slug):
    item=Stores.objects.get(slug=slug)
    if request.method=='POST':
        item.delete()
        return redirect('crm:store_list')
    else:
        return render(request, 'stores/store_delete.html', context={'item':item})

class StoreItem(DetailView):
    model = Stores
    context_object_name = 'item'
    template_name = 'stores/store_details.html'

class BrandAdd(CreateView):
    form_class = BrandForm
    template_name = 'brands/brand_add.html'
    def form_valid(self, form):
        Brands.objects.create(**form.cleaned_data)
        return redirect('crm:brand_list')

def supplier_list(request):
    supp_list=Suppliers.objects.all()
    return render(request, 'suppliers/suppliers_list.html', context={'supp_list': supp_list})

def supplier_details(request, slug):
    supp_detail=Suppliers.objects.get(slug=slug)
    return render(request, 'suppliers/supplier_detail.html', context={'supp_detail': supp_detail})

def supplier_add(request):

    if request.method=='POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            Suppliers.objects.create(**form.cleaned_data)
            return redirect('crm:suppliers_list')
    else:
        form = SupplierForm()
        return render(request, 'suppliers/supplier_add.html', context={'form': form})

class SupplierDelete(DeleteView):
    model=Suppliers
    context_object_name = 'item'
    template_name = 'suppliers/supplier_delete.html'
    success_url = reverse_lazy('crm:suppliers_list')

class CataloModelDelete(DeleteView):
    model = Catalog
    context_object_name = 'item'
    template_name = 'catalogModels/catalog_model_delete.html'
    success_url = reverse_lazy('crm:catalog_list')

def catalogModels_add(request):

    if request.method=='POST':
        form = CatalogForm(request.POST)
        if form.is_valid():
            new_obj=form.save()
            return redirect(new_obj)
    else:
        form = CatalogForm()
        return render(request, 'catalogModels/catalog_model_add.html', context={'form': form})

class BrandEdit(UpdateView):
    model = Brands
    context_object_name = 'brand'
    template_name = 'crmApp/brands/brand_edit.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('crm:brand_list')

def supplierEdit(request, slug):
    obj=Suppliers.objects.get(slug=slug)
    if request.method=='POST':
        form=SupplierForm(request.POST)
        if form.is_valid():
            obj.name=form.cleaned_data['name']
            obj.slug=form.cleaned_data['slug']
            newobj=obj.save()
            return redirect('crm:suppliers_list')
    else:
        form = SupplierForm({'name': obj.name, 'slug': obj.slug})
        return render(request, 'suppliers/supplier_edit.html', context={'form': form})

def catalogModelEdit(request, slug):
    obj=Catalog.objects.get(slug=slug)
    if request.method=='POST':
        form=CatalogForm(request.POST, instance=obj)
        if form.is_valid():
            update_obj=form.save()
            return redirect(update_obj)

    else:
        form=CatalogForm(instance=obj)
        return render(request, 'catalogModels/catalog_model_edit.html', context={'form': form})

class StoreEdit(UpdateView):
    model = Stores
    context_object_name = 'item'
    template_name = 'crmApp/stores/stores_edit.html'
    fields = ['catalog_item', 'quantity', 'wholesale_price', 'supplier', 'slug']
    success_url = reverse_lazy('crm:store_list')


# def userLogin(request):
#     if request.method=='POST':
#         form=LoginForm(request.POST)
#         if form.is_valid():
#             username=form.cleaned_data['username']
#             psw=form.cleaned_data['password']
#             user=authenticate(request, username=username, password=psw)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     url=request.GET.get('next','')
#                     return redirect(settings.LOGIN_REDIRECT_URL if url=='' else url)
#                 else:
#                     return HttpResponse('Юзер не активен')
#             else:
#                 return HttpResponse('Облом')
#         else: return HttpResponse(form.errors)
#     else:
#         form=LoginForm()
#         return render(request, 'registration/login.html', context={'form':form})
#
# def userLogout(request):
#     logout(request)
#     return HttpResponse('разлогинился')


@login_required
def dashboard(request):

    if request.method=='GET':
        form=DashBoardForm(initial={'depthDaysOrders':1, 'depthDaysProducts':3})

    else:
        form=DashBoardForm(request.POST)
        if form.is_valid():
            a = serviceAli()
            if form.cleaned_data['checkBoxOrders']:
                a.updateOrderList(int(form.data['depthDaysOrders']))
            if form.cleaned_data['checkBoxProducts']:
                a.updateProducts(int(form.data['depthDaysProducts']))
            if form.cleaned_data['checkBoxGroups']:
                a.updateGroupList()
            if form.cleaned_data['checkBoxMyOwnProducts']:
                handle_myownstore()
            if form.cleaned_data['checkBoxImportTradeChas']:
                handle_tradechas()
            if form.cleaned_data['checkBoxAvangardProducts']:
                handle_AvangardProducts()
            if form.cleaned_data['checkBoxSendToAli']:
                    handle_syncInventory()


    return render(request,'dashboard/dashboard.html', context={'form':form, 'active_page':'dashboard'})

def userNew(request):
    if request.method=='POST':
        form=UserRegForm(request.POST)
        if form.is_valid():
            new_user=form.save()
            login(request, new_user)
            return render(request, 'registration/newUserDone.html')
    else:
        form=UserRegForm()
    return render(request, 'registration/newUser.html', context={'form':form})


class ProductsList(ListView):
    model=AliProducts
    context_object_name = 'productsList'
    template_name = 'products-list/products_list.html'
    paginate_by = 10
    paginate_orphans = 5
    ordering='-gmt_create'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'productlist'
        return context


def productInfoDetail(request, id):
    try:
        product_detail = AliProducts.objects.get(product_id=id) # краткая информация из пакетной функции из БД
        a=serviceAli()
        productDetailInfo=a.getProduct(id) # детальная информация из одиночной функции из API
        skulist=productDetailInfo['aeop_ae_product_s_k_us']['global_aeop_ae_product_sku']
        return render(request, context={'product_info': product_detail, 'product_detail_info': productDetailInfo, 'skulist':skulist},
                      template_name='products-list/product_info.html')

    except Exception as err:
        print(f' ошибка: {err}')
        return redirect('crm:products_list')

class OrderList(ListView):
    model=AliOrders
    # context_object_name = 'orderList'
    template_name = 'orders/orders_list.html'
    ordering='-gmt_create'
    paginate_orphans=5
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'orderlist'
        return context


@check_funcs
def OrderInfoDetail(request, id):
    def list_of_choises(): # делаем списки для выбора ПВЗ в выпадающем меню
        for i in DEPARTURE_CITIES:
            form.fields[i['id']].choices=list(map(lambda x: (x['info']['id'], x['info']['name'] + ' - ' + x['result']['price']),
                       orderDetailInfo.cdektarif_tarifes[i['id']]))
        form.fields['selectPVZ'].choices = list(map(lambda x: (x['code'], x['location']['address']), orderDetailInfo.cdek_pvz))
    orderDetailInfo=orderAliInfo(id)
    # print(orderDetailInfo.aliordersproductlist_product_name)
    if request.method=='GET':
        if orderDetailInfo.cdek_isPVZ==1: # если есть ПВЗ, то у нас форма с ПВЗ
            form = OrderInfoForm(initial={'recieverFIO':orderDetailInfo.alidetailinfo_receipt_address['contact_person'], 'insurance':0})
        else: # иначе спецаильная форма без ПВЗ
            form = OrderInfoFormNonPVZ(initial={'recieverFIO': orderDetailInfo.alidetailinfo_receipt_address['contact_person'], 'insurance': 0})
        list_of_choises()
        return render(request, context={'order_info': orderDetailInfo, 'form': form},
                      template_name='orders/order_info.html')
    else: # если метод POST , значит нажали кнопку получения накладной
        _isPVZ=orderDetailInfo.cdek_isPVZ==1
            # если есть ПВЗ, то у нас форма с ПВЗ, иначе специальная форма без ПВЗ
        form=OrderInfoForm(request.POST) if _isPVZ else OrderInfoFormNonPVZ(request.POST)
        list_of_choises()
        if form.is_valid:
            # создаём набор данных для накладной СДЭК
            d = dict()
            selectedShippingFrom=form.data['selectShippingFrom']
            d['tariff_code'] =form.data[selectedShippingFrom]
            d['name'] = form.data['recieverFIO']
            if _isPVZ:
                d['delivery_point'] =form.data['selectPVZ'] # если есть ПВЗ, то заполняется ПВЗ
            else: # если нет, то заполняется адрес, оба сразу нельзя.
                # Надо доделать, что если тариф до дома, то адрес должен заполняться, а не ПВЗ
                d['to_location']={'address':orderDetailInfo.pochta_normalized_address.get('street','')+
                                        ','+orderDetailInfo.pochta_normalized_address.get('house','')+
                                        ','+orderDetailInfo.pochta_normalized_address.get('room',''),
                                  'postal_code':orderDetailInfo.pochta_normalized_address['index']}
            d['phone'] = orderDetailInfo.alidetailinfo_receipt_address['phone_country']+orderDetailInfo.alidetailinfo_receipt_address['mobile_no']
            d['packages'] = orderDetailInfo.product_list_for_cdek(form.data['insurance'])
            d['number'] = orderDetailInfo.order_id
            # подбираем ПВЗ по выбранному городу отправки
            d['shipment_point']=next((x['PVZ'] for x in DEPARTURE_CITIES if x['id']==selectedShippingFrom), None)
            newO = CdekOrder(**d) # добавление постоянных данных
            cdek = CdekAPI(client_id=Account, client_secret=Secure_password)
            result = cdek.new_order(newO)
            orderDetailInfo.cdek_response_save(result)
            print(result)
            return render(request, context={'order_info': orderDetailInfo, 'form': form},
                      template_name='orders/order_info.html')


# def import_avangard(request):
#     if request.method=="POST":
#         form=UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_avangard_file(request.FILES['file'])
#             print(f'Загружен файл {request.FILES["file"]}')
#             # s = AvangardApi()
#             # s.updating_stocks()
#     else:
#         form=UploadFileForm()
#     # importTradeChas.handled_data()
#     # importMyStock.handled_data()
#     # syncVostokInventory()
#     return render(request, context={'form':form, 'active_page':'importpage'}, template_name='products-list\load-avangard.html')

def importMyOwn(request):
    handle_myownstore()
    return HttpResponse('готово')

def importTradechas(request):
    handle_tradechas()
    return HttpResponse('готово')

def syncInventory(request):
    handle_syncInventory()
    return HttpResponse('готово')

def getInventorySyncResults(request, jobid):
    handle_getsyncInventoryResults(jobid)
    return HttpResponse('готово')

def impoRTAvangardProducts(request):
    handle_AvangardProducts()
    return HttpResponse('готово')
