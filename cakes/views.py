from django.shortcuts import render
from .models import Cake, Ingredients, Level, Form, DeliveryType, OrderStatus, Order, DeliveryTime, Client

# Create your views here.
def index(request):
    cakes = Cake.objects.all()
    return render(request, 'index.html', context={'cakes': cakes})
