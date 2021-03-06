from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(Brands)
admin.site.register(Series)
# admin.site.register(Catalog)
admin.site.register(Suppliers)
# admin.site.register(Stores)

# admin.site.register(AliOrders)
admin.site.register(AliOrdersProductList)
admin.site.register(AliProducts)

@admin.register(AliOrders)
class AliOrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'logistics_status', 'gmt_create')



@admin.register(Brands)
class BrandsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('article', 'brand_name', 'model_name', 'stock', 'stock_suppl')
    list_filter = ('brand_name',)
    ordering = ('-model_name',)

@admin.register(Stores)
class StoresAdmin(admin.ModelAdmin):
    list_display = ('catalog_item','quantity', 'supplier')
    list_filter = ('supplier',)
