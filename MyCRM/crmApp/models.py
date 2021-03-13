from djmoney.models.fields import MoneyField
from django.db import models
from django.urls import reverse
from django.db.models import Sum



# Сущность Бренды
class Brands(models.Model):
    name=models.CharField(max_length=20) # поле наимнование бренда
    description=models.TextField(max_length=200, blank=True)
    slug=models.SlugField(unique=True) # путь к страничке бренда
    def __str__(self):
         return self.name
    def get_absolute_url(self):
        return reverse('crm:brand_details', args=[self.slug])
    class Meta:
        verbose_name='Бренд'
        verbose_name_plural='Бренды'

# Сущность Серии, к которым относится модель
class Series(models.Model):
    name=models.CharField(max_length=20) # Наименование серии
    def __str__(self):
        return self.name
    class Meta:
        verbose_name='Серия'
        verbose_name_plural='Серии'

# Сущность Каталог моделей какие вообще бывают в природе
class Catalog(models.Model):
    article=models.CharField(max_length=15, unique=True, help_text='артикул товара') # артикул, уникальное поле
    brand_name=models.ForeignKey(Brands, on_delete=models.DO_NOTHING,
                                 related_name='catalog_items') # связь с сущностью Бренды
    model_name=models.CharField(max_length=15, help_text='модель') # Наименование модели
    model_series=models.ManyToManyField(Series, blank=True) # связь с сущностью Серии
    def __str__(self):
        return self.brand_name.name+' '+self.model_name
    def get_absolute_url(self):
        return reverse('crm:model_details', args=[self.article])
    def stock(self): # общее кол-во в остатке
        return self.item_of_store.aggregate(Sum('quantity'))['quantity__sum']
    def stock_suppl(self): # остатки в разрезе поставщиков
        a=self.item_of_store.all()
        return {i.supplier.name:i.quantity for i in a if i.quantity>0}

    class Meta:
        verbose_name='Модель'
        verbose_name_plural='Каталог моделей'


# Сущность поставщики
class Suppliers(models.Model):
    name=models.CharField(max_length=20, verbose_name='Наименование поставщика') # Наименование поставщика
    slug=models.SlugField(unique=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('crm:suppliers_details', args=[self.slug])
    class Meta:
        verbose_name='поставщик'
        verbose_name_plural='Поставщики'

# Сущность информация по остаткам и ценам на складах у поставщиков
class Stores(models.Model):
    catalog_item=models.ForeignKey(Catalog, related_name='item_of_store', on_delete=models.CASCADE, verbose_name='Модель')
    quantity=models.IntegerField(blank=True, verbose_name='количество')
    wholesale_price=MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', blank=True, verbose_name='оптовая цена')
    supplier=models.ForeignKey(Suppliers,on_delete=models.CASCADE, related_name='items_of_supplier', verbose_name='поставщик')
    innerID=models.CharField(verbose_name="inner suppliers product id", max_length=20, blank=True, default='')
    def __str__(self):
         return self.supplier.name
    class  Meta:
        verbose_name='Складской запас'
        verbose_name_plural='Складские запасы'

class AliProducts(models.Model):
    ws_offline_date=models.DateTimeField(verbose_name='product offline time', null=True)
    ws_display=models.CharField(verbose_name='product offline reason', max_length=8, blank=True, default='')
    subject=models.CharField(verbose_name='product title', max_length=150)
    src=models.CharField(verbose_name='product src', max_length=8)
    product_min_price=models.CharField(verbose_name='min price among all skus of the product', max_length=10, blank=True, default='')
    product_max_price=models.CharField(verbose_name='max price among all skus of the product', max_length=10, blank=True, default='')
    product_id=models.PositiveIntegerField(primary_key=True)
    owner_member_seq=models.PositiveIntegerField(verbose_name='seller member seq')
    owner_member_id=models.CharField(verbose_name='seller login id', max_length=8)
    image_u_r_ls=models.URLField(verbose_name='product image url')
    group_id=models.IntegerField(verbose_name='Search field by product groups. Enter product group id (groupId)')
    gmt_modified=models.DateTimeField(verbose_name='time that product was modifed')
    gmt_create=models.DateTimeField(verbose_name='time that product was created')
    freight_template_id=models.PositiveIntegerField(verbose_name='freight template id')
    currency_code=models.CharField(verbose_name='currency code', max_length=3)
    coupon_start_date=models.DateTimeField(verbose_name='Coupon start date, GMT+8', null=True)
    coupon_end_date = models.DateTimeField(verbose_name='Coupon end date, GMT+8', null=True)
    # def __str__(self):
    #     return self.subject


class AliOrders(models.Model):
    timeout_left_time=models.IntegerField(verbose_name='The remain time of the current status ',null=True)
    seller_signer_fullname=models.CharField(max_length=10, verbose_name='seller fuller name')
    seller_operator_login_id=models.CharField(max_length=10, verbose_name='seller operator login id')
    seller_login_id=models.CharField(max_length=10, verbose_name='seller login id')
    phone=models.BooleanField(verbose_name='Whether mobile phone orders')
    payment_type=models.CharField(max_length=15, verbose_name='pay type', blank=True, default='')
    pay_amount=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='pay amount', max_length=8, null=True)
    order_status=models.CharField(max_length=15, verbose_name='order status')
    order_id=models.PositiveIntegerField(verbose_name='order ID', primary_key=True)
    order_detail_url=models.URLField(verbose_name='order detail url')
    logistics_status=models.CharField(verbose_name='logistics status', max_length=20)
    logisitcs_escrow_fee_rate=models.CharField(verbose_name='logistics escrow fee rate', max_length=5)
    loan_amount=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='loan amount details', max_length=8, null=True)
    left_send_good_min=models.CharField(verbose_name='Remaining delivery time (minute)', max_length=2, blank=True, default='')
    left_send_good_hour=models.CharField(verbose_name='Remaining delivery time (hour)', max_length=2, blank=True, default='')
    left_send_good_day=models.CharField(verbose_name='Remaining delivery time (days)', max_length=3, blank=True, default='')
    issue_status=models.CharField(verbose_name='issue status', max_length=15)
    has_request_loan=models.BooleanField(verbose_name='Have you requested a loan?')
    gmt_update=models.DateTimeField(verbose_name='Last order update time')
    gmt_send_goods_time=models.DateTimeField(verbose_name='Last order delivery time',null=True)
    gmt_pay_time=models.DateTimeField(verbose_name='order pay time', null=True)
    gmt_create=models.DateTimeField(verbose_name='order create time')
    fund_status=models.CharField(verbose_name='fund status', max_length=15)
    frozen_status=models.CharField(verbose_name='frozen status', max_length=15)
    escrow_fee_rate=models.PositiveIntegerField(verbose_name='escrow fee rate', null=True)
    escrow_fee=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='escrow fee', max_length=8, null=True)
    end_reason=models.CharField(verbose_name='order finished reason', max_length=15)
    buyer_signer_fullname=models.CharField(verbose_name='buyer full name', max_length=30)
    buyer_login_id=models.CharField(verbose_name='buyer login id', max_length=30)
    biz_type=models.CharField(verbose_name='order type', max_length=15)
    offline_pickup_type=models.CharField(verbose_name='pickup type of order', max_length=15)
    def __str__(self):
        return self.buyer_signer_fullname

    def products_list_names(self):
        a=AliOrdersProductList.objects.filter(main_order=self.order_id)
        e=[i.product_name for i in a]
        g='| '.join(e)
        return g

class AliOrdersDetailedInformation(models.Model):
    order=models.OneToOneField(AliOrders, on_delete=models.CASCADE, primary_key=True)
    buyer_info=models.CharField(verbose_name="buyer info", max_length=100)
    gmt_modified=models.DateTimeField(verbose_name='modified time, US pacific time', null=True)
    gmt_create = models.DateTimeField(verbose_name='время создания заказа', null=True)
    receipt_address=models.CharField(verbose_name="receipt address", max_length=200)
    gmt_trade_end=models.DateTimeField(verbose_name='Order end time', null=True)
    buyerloginid=models.CharField(verbose_name="buyer login id", max_length=30)
    order_status=models.CharField(verbose_name="Order Status", max_length=30)
    coord=models.CharField(verbose_name='Координаты адреса покупателя', max_length=30, blank=True, default='')
    normalized_address=models.CharField(verbose_name='Нормализованный адрес', max_length=180, blank=True, default='')
    full_normalized_address=models.CharField(verbose_name='Полный нормализованный адрес', max_length=180, blank=True, default='')
    pvz=models.CharField(verbose_name='СДЕК ПВЗ в городе покупателя', max_length=2000, blank=True, default='')
    tarifes=models.CharField(verbose_name='Тарифы СДЭК', max_length=500, blank=True, default='')
    isPVZ=models.PositiveIntegerField(verbose_name='Есть ПВЗ в городе', null=True)
    cdekResponse=models.CharField(verbose_name='Ответ от СДЭК', max_length=100, blank=True, default='')
    cdekStatus=models.CharField(verbose_name='Статус посылки СДЭК', max_length=100, blank=True, default='')

class tokensApi(models.Model):
    nameApi=models.CharField(max_length=10, verbose_name='API имя', primary_key=True)
    token=models.BinaryField(verbose_name='Токен', blank=True)
    data_expires=models.DateTimeField(verbose_name='Дата действия токена', null=True)

class AliOrdersProductList(models.Model):
    main_order=models.ForeignKey(AliOrders, on_delete=models.PROTECT,  related_name='products_list')
    total_product_amount=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='total product amount', max_length=8)
    son_order_status=models.CharField(verbose_name='child order status', max_length=15)
    sku_code=models.CharField(verbose_name='sku code', max_length=15)
    show_status=models.CharField(verbose_name='order show status', max_length=15)
    send_goods_time=models.DateTimeField(verbose_name='Last delivery time', null=True)
    send_goods_operator=models.CharField(verbose_name='Shipper type', max_length=25)
    product_unit_price=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='product unit price', max_length=8)
    product_unit=models.CharField(verbose_name='product unit', max_length=15)
    product_standard=models.CharField(verbose_name='product standard', max_length=15)
    product_snap_url=models.URLField(verbose_name='product snap Url')
    product_name=models.CharField(verbose_name='product name', max_length=150)
    product_img_url=models.URLField(verbose_name='product main image url')
    product=models.ForeignKey(AliProducts, on_delete=models.PROTECT)
    product_count=models.PositiveIntegerField(verbose_name='product count')
    order_id=models.PositiveIntegerField(verbose_name='sub order id ', primary_key=True)
    money_back3x=models.BooleanField(verbose_name='fake one compensate three flag')
    memo=models.CharField(verbose_name='buyer memo', max_length=15)
    logistics_type=models.CharField(verbose_name='logistics service name( key)', max_length=15)
    logistics_service_name=models.CharField(verbose_name='logistics service show name)', max_length=15)
    logistics_amount=MoneyField(max_digits=7,decimal_places=2, default_currency='RUB',verbose_name='Logistics amount(sub-orders have no shipping costs, please ignore)', max_length=8)
    issue_status=models.CharField(verbose_name='issue status (NO_ISSUE; IN_ISSUE; END_ISSUE)', max_length=15)
    issue_mode=models.CharField(verbose_name='issue mode', max_length=15)
    goods_prepare_time=models.PositiveIntegerField(verbose_name='goods prepare days')
    fund_status=models.CharField(verbose_name='fund status', max_length=15)
    freight_commit_day=models.CharField(verbose_name='Limited time', max_length=15)
    escrow_fee_rate=models.CharField(verbose_name='escrow fee rate', max_length=15)
    delivery_time=models.CharField(verbose_name='delivery time', max_length=15)
    child_id=models.PositiveIntegerField(verbose_name='child order id')
    can_submit_issue=models.BooleanField(verbose_name='Whether child orders can submit disputes')
    buyer_signer_last_name=models.CharField(verbose_name='buyer last name', max_length=50)
    buyer_signer_first_name=models.CharField(verbose_name='buyer first name', max_length=50)
    afflicate_fee_rate=models.CharField(verbose_name='afflicate fee rate', max_length=7)



class AliGroupList(models.Model):
    group_name=models.CharField(verbose_name='group name', max_length=20)
    group_id=models.PositiveIntegerField(verbose_name='group id', primary_key=True)
    hasChild=models.BooleanField(verbose_name='item has subgroup', default=False)

class AliChildGroupList(models.Model):
    group_name = models.CharField(verbose_name='group name', max_length=20)
    group_id = models.PositiveIntegerField(verbose_name='group id', primary_key=True)
    ali_group=models.ForeignKey(AliGroupList, on_delete=models.CASCADE)


class ProductsSKU(models.Model):
    SPU=models.ForeignKey(AliProducts, on_delete=models.CASCADE,
                          verbose_name='product id', related_name='product')
    SKU=models.CharField(verbose_name='SKU',max_length=15)
    brand=models.CharField(verbose_name='brand in ALi',max_length=15, blank=True, default='')
    model=models.CharField(verbose_name='model in ALi',max_length=15, blank=True, default='')
    subject=models.CharField(verbose_name='subject in Russian',max_length=50, blank=True, default='')
    class Meta:
        unique_together = (('SPU', 'SKU'),)

class AliFeedOperations(models.Model):
    jobID=models.PositiveIntegerField(primary_key=True)
    timeOperation=models.TimeField(auto_now_add=True)
    request_id=models.CharField(max_length=10, unique=True)

class AliFeedOperationsLog(models.Model):
    job=models.ForeignKey(AliFeedOperations, on_delete=models.CASCADE)
    item_content_id=models.CharField(max_length=15)
    item_execution_result=models.CharField(max_length=250,blank=True, default='' )

    class Meta:
        unique_together = (('job', 'item_content_id'),)


