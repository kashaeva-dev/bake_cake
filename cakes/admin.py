from django.contrib import admin

from cakes.models import (
    Client,
    Ingredients,
    Level,
    Form,
    Cake,
    DeliveryType,
    OrderStatus,
    Order,
    DeliveryTime,
    IngredientCategory,
)


admin.site.register(Client)
admin.site.register(Ingredients)
admin.site.register(Level)
admin.site.register(Form)
admin.site.register(Cake)
admin.site.register(DeliveryType)
admin.site.register(OrderStatus)
admin.site.register(Order)
admin.site.register(DeliveryTime)
admin.site.register(IngredientCategory)
