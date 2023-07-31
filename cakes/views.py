from django.shortcuts import render

from .models import (
    Cake,
    Ingredients,
    IngredientCategory, Client, Order,
)


# Create your views here.
def index(request):
    cakes = Cake.objects.filter(standard=True)
    return render(request, 'cakes/index.html', context={'cakes': cakes})


def toppings(request):
    category = IngredientCategory.objects.filter(name='Топпинг')[0]
    toppings = Ingredients.objects.filter(category=category)
    return render(request, 'cakes/toppings.html', context={'toppings': toppings})


def berries(request):
    category = IngredientCategory.objects.filter(name='Ягоды')[0]
    berries = Ingredients.objects.filter(category=category)
    return render(request, 'cakes/berries.html', context={'berries': berries})


def decoration(request):
    category = IngredientCategory.objects.filter(name='Декор')[0]
    decorations = Ingredients.objects.filter(category=category)
    return render(request, 'cakes/decoration.html', context={'decorations': decorations})


def my_cakes(request, chat_id):
    client = Client.objects.get(chat_id=chat_id)
    client_cakes_ids = Order.objects.filter(client=client).values_list('cake', flat=True)
    client_cakes = Cake.objects.filter(id__in=client_cakes_ids).distinct()

    return render(request, 'cakes/my_cakes.html', context={'cakes': client_cakes})
