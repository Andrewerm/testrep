from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from .models import Brands

app_name='crm'

urlpatterns=[
    path('accounts/newUser', views.userNew, name='new_user'),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('login',views.userLogin, name='login'),
    # path('logout',views.userLogout, name='logout'),
    path('brands/add', views.BrandAdd.as_view(), name='brand_add'),
    path('brands/delete/<slug:slug>', views.BrandDelete.as_view(), name='brand_del'),
    path('brands/update/<slug:slug>', views.BrandEdit.as_view(), name='brand_edit'),
    path('brands/<slug:slug>', views.BrandDetail.as_view(), name='brand_details'),
    path('brands/', views.BrandsView.as_view(model=Brands, context_object_name='brands', template_name='crmApp/brands/brands_list.html'), name='brand_list'),
    path('catalog/add', views.catalogModels_add, name='catalog_model_add'),
    path('catalog/delete/<slug:slug>', views.CataloModelDelete.as_view(), name='model_delete'),
    path('catalog/edit/<slug:slug>', views.catalogModelEdit, name='model_edit'),
    path('catalog/<slug:slug>', views.CatalogModelDetail.as_view(), name='model_details'),
    path('catalog/', views.CatalogView.as_view(), name='catalog_list'),
    path('store/add', views.store_add, name='store_add'),
    path('store/delete/<slug:slug>', views.store_delete, name='store_delete'),
    path('store/edit/<slug:slug>', views.StoreEdit.as_view(), name='store_edit'),
    path('store/<slug:slug>', views.StoreItem.as_view(), name='store_item'),
    path('store/', views.StoresList.as_view(), name='store_list'),
    path('suppliers/add', views.supplier_add, name='suppliers_add'),
    path('suppliers/<slug:slug>', views.supplier_details, name='suppliers_details'),
    path('suppliers/delete/<slug:slug>', views.SupplierDelete.as_view(), name='supplier_delete'),
    path('suppliers/edit/<slug:slug>', views.supplierEdit, name='supplier_edit'),
    path('suppliers/', views.supplier_list, name='suppliers_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('dashboard2/', views.dashboard2, name='dashboard2'),
    # path('dashboard/pressImportOrders/', views.pressButImportOrders, name='pressImportOrder'),
    path('product_list/', views.ProductsList.as_view(), name='products_list'),
    path('product_info_view/<int:id>', views.productInfoDetail, name='product_info'),
    # path('orders_list/', views.orderList, name='orders_list'),
    path('orders_list/', views.OrderList.as_view(), name='orders_list'),
    # path('order_info/createCdekOrder/<int:id>', views.createCdekOrder, name='create_cdek_order'),
    path('order_info/<int:id>', views.OrderInfoDetail, name='order_info'),
    # path('order_info/<int:id>', views.OrderInfoDetail.as_view(), name='order_info'),
    path('load_avangard/', views.import_avangard,  name="import_avangard"),
    path('importmyown/', views.importMyOwn, name="import_myown"),
    path('importtraid/', views.importTradechas, name="import_trade"),
    path('syncinventory/', views.syncInventory, name="syncinventory"),
    path('syncinventoryresponce/<int:jobid>', views.getInventorySyncResults, name="getInventorySyncResults"),
]