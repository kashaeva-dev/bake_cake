from django.db import models


class Advertisement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название кампании', null=True)
    refer_id = models.PositiveSmallIntegerField(verbose_name='Telegram ID кампании')
    refer_url = models.URLField(verbose_name='Ссылка на кампанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Рекламная кампания'
        verbose_name_plural = 'Рекламные кампании'


class Client(models.Model):
    chat_id = models.PositiveBigIntegerField(verbose_name='ID чата клиента')
    first_name = models.CharField(max_length=40, verbose_name='Имя клиента', null=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    personal_data_consent = models.BooleanField(verbose_name='Согласие на обработку персональных данных')
    personal_data_consent_date = models.DateTimeField(auto_now_add=True,
                                                      verbose_name='Дата согласия на ОПД',
                                                      blank=True,
                                                      null=True,
                                                      )
    advertisement = models.ForeignKey(Advertisement,
                                      on_delete=models.PROTECT,
                                      verbose_name='Рекламная кампания',
                                      null=True,
                                      blank=True,
                                      related_name='clients',
                                      )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.chat_id}: {self.first_name}'


class Ingredients(models.Model):
    category = models.CharField(max_length=40, verbose_name='Категория')
    name = models.CharField(max_length=40, verbose_name='Название')
    picture = models.ImageField(upload_to='components', verbose_name='Изображение')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Level(models.Model):
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество уровней')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Form(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название формы')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Cake(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название торта')
    description = models.TextField(verbose_name='Описание')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, verbose_name='Количество уровней')
    form = models.ForeignKey(Form, on_delete=models.PROTECT, verbose_name='Форма')
    weight = models.PositiveSmallIntegerField(verbose_name='Вес, кг')
    picture = models.ImageField(upload_to='cakes', verbose_name='Изображение')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Tорт'
        verbose_name_plural = 'Tорты'

    def __str__(self):
        return f'{self.name}'


class DeliveryType(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class OrderStatus(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Клиент')
    cake = models.ForeignKey(Cake, on_delete=models.PROTECT, verbose_name='Торт')
    ingredients = models.ManyToManyField(Ingredients, verbose_name='Ингредиенты')
    inscription = models.CharField(max_length=40, verbose_name='Надпись', null=True, blank=True)
    cake_comment = models.TextField(verbose_name='Комментарий к торту')
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, verbose_name='Статус заказа')
    total_cake_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена торта')
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT, verbose_name='Тип доставки')
    total_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена доставки')
    delivery_address = models.CharField(max_length=40, verbose_name='Адрес доставки')
    delivery_comment = models.TextField(verbose_name='Комментарий к доставке')
    delivery_man_name = models.CharField(max_length=40, verbose_name='Курьер', null=True, blank=True)
    delivery_man_phonenumber = models.CharField(max_length=40,
                                                verbose_name='Номер телефона курьера',
                                                null=True,
                                                blank=True
                                                )
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        delivery_time_obj = self.delivery_time.first()
        if delivery_time_obj:
            planned_delivery_date = delivery_time_obj.delivery_date
            planned_delivery_time = delivery_time_obj.delivery_time.strftime('%H:%M')
            if self.delivery_address:
                return f'{self.cake} - {self.cake.weight}: плановая доставка {planned_delivery_date.date} ' \
                       f'{planned_delivery_time} по адресу: {self.delivery_address}'
            else:
                return f'{self.cake}: {self.delivery_type.name}' \
                       f' {planned_delivery_date.date()} с {planned_delivery_time}'
        else:
            if self.delivery_address:
                return f'{self.cake} - {self.weight}: доставка по адресу: {self.delivery_address}'
            else:
                return f'{self.cake}: {self.delivery_type.name}'


class DeliveryTime(models.Model):
    DELIVERY_STATUS_CHOICES = (
        ('initial', 'План'),
        ('changed', 'Изменение'),
        ('delivered', 'Факт'),
    )
    order = models.ForeignKey(Order,
                              on_delete=models.PROTECT,
                              verbose_name='Заказ',
                              related_name='delivery_time'
                              )
    delivery_date = models.DateTimeField(verbose_name='Дата доставки')
    delivery_time = models.TimeField(verbose_name='Время доставки')
    delivery_status = models.CharField(max_length=40,
                                       verbose_name='Статус доставки',
                                       choices=DELIVERY_STATUS_CHOICES,
                                       )
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)

