# Generated by Django 4.2.3 on 2023-07-26 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Название кампании')),
                ('refer_id', models.PositiveSmallIntegerField(verbose_name='Telegram ID кампании')),
                ('refer_url', models.URLField(verbose_name='Ссылка на кампанию')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Рекламная кампания',
                'verbose_name_plural': 'Рекламные кампании',
            },
        ),
        migrations.CreateModel(
            name='Cake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название торта')),
                ('description', models.TextField(verbose_name='Описание')),
                ('weight', models.PositiveSmallIntegerField(verbose_name='Вес, кг')),
                ('picture', models.ImageField(upload_to='cakes', verbose_name='Изображение')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
            options={
                'verbose_name': 'Стандартный торт',
                'verbose_name_plural': 'Стандартные торты',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.PositiveBigIntegerField(verbose_name='ID чата клиента')),
                ('first_name', models.CharField(max_length=40, null=True, verbose_name='Имя клиента')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('personal_data_consent', models.BooleanField(verbose_name='Согласие на обработку персональных данных')),
                ('personal_data_consent_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата согласия на ОПД')),
                ('advertisement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clients', to='cakes.advertisement', verbose_name='Рекламная кампания')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='DeliveryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название формы')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=40, verbose_name='Категория')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
                ('picture', models.ImageField(upload_to='components', verbose_name='Изображение')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='Количество уровней')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inscription', models.CharField(blank=True, max_length=40, null=True, verbose_name='Надпись')),
                ('cake_comment', models.TextField(verbose_name='Комментарий к торту')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('total_cake_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена торта')),
                ('total_delivery_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена доставки')),
                ('delivery_address', models.CharField(max_length=40, verbose_name='Адрес доставки')),
                ('delivery_comment', models.TextField(verbose_name='Комментарий к доставке')),
                ('delivery_man_name', models.CharField(blank=True, max_length=40, null=True, verbose_name='Курьер')),
                ('delivery_man_phonenumber', models.CharField(blank=True, max_length=40, null=True, verbose_name='Номер телефона курьера')),
                ('cake', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.cake', verbose_name='Торт')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.client', verbose_name='Клиент')),
                ('delivery_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.deliverytype', verbose_name='Тип доставки')),
                ('ingredients', models.ManyToManyField(to='cakes.ingredients', verbose_name='Ингредиенты')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.orderstatus', verbose_name='Статус заказа')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='DeliveryTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateTimeField(verbose_name='Дата доставки')),
                ('delivery_time', models.TimeField(verbose_name='Время доставки')),
                ('delivery_status', models.CharField(choices=[('initial', 'План'), ('changed', 'Изменение'), ('delivered', 'Факт')], max_length=40, verbose_name='Статус доставки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='delivery_time', to='cakes.order', verbose_name='Заказ')),
            ],
        ),
        migrations.AddField(
            model_name='cake',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.form', verbose_name='Форма'),
        ),
        migrations.AddField(
            model_name='cake',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cakes.level', verbose_name='Количество уровней'),
        ),
    ]