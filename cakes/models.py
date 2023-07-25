from django.db import models


class Advertisement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название кампании', null=True, blank=True)
    telegram_id = models.IntegerField(max_length=5, verbose_name='Telegram ID кампании')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Рекламная кампания'
        verbose_name_plural = 'Рекламные кампании'


class Client(models.Model):
    chat_id = models.CharField(max_length=20, verbose_name='ID чата клиента')
    first_name = models.CharField(max_length=40, verbose_name='Имя клиента', null=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    personal_data_consent = models.BooleanField(verbose_name='Согласие на обработку персональных данных')
    personal_data_consent_date = models.DateTimeField(auto_now_add=True,
                                                      verbose_name='Дата согласия на ОПД',
                                                      blank=True,
                                                      null=True,
                                                      )
    advertisement = models.ForeignKey(Advertisement,
                                      on_delete=models.CASCADE,
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
    quantity = models.IntegerField(max_length=2, verbose_name='Количество уровней')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Form(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название формы')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Cake(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название торта')
    description = models.TextField(verbose_name='Описание')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name='Количество уровней')
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name='Форма')
    picture = models.ImageField(upload_to='cakes', verbose_name='Изображение')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Стандартный торт'
        verbose_name_plural = 'Стандартные торты'

    def __str__(self):
        return f'{self.name}'


class DeliveryType(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')


class Status(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')


class DeliveryInterval(models.Model):
    start_time = models.TimeField(verbose_name='Начало интервала')
    end_time = models.TimeField(verbose_name='Конец интервала')


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, verbose_name='Торт')
    ingredients = models.ManyToManyField(Ingredients, verbose_name='Ингредиенты')
    inscription = models.CharField(max_length=40, verbose_name='Надпись', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True)
    delivery_date = models.DateTimeField(verbose_name='Дата доставки')
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='Тип доставки')
    delivery_interval = models.ForeignKey(DeliveryInterval, on_delete=models.CASCADE, verbose_name='Интервал доставки')
    delivery_address = models.CharField(max_length=40, verbose_name='Адрес доставки')
    delivery_comment = models.TextField(verbose_name='Комментарий к доставке')
    total_cake_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена торта')
    total_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена доставки')
    delivery_man_name = models.CharField(max_length=40, verbose_name='Курьер', null=True, blank=True)
    delivery_man_phonenumber = models.CharField(max_length=40, verbose_name='Номер телефона курьера', null=True, blank=True)
    status = models.CharField(max_length=40, verbose_name='Статус заказа')
