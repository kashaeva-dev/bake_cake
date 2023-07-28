from django.shortcuts import render

from .models import (
    Cake,
    Ingredients,
    IngredientCategory,
)


# Create your views here.
def index(request):
    cakes = Cake.objects.all()
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
