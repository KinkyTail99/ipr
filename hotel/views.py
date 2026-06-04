import io
import base64
import requests
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import Room, Booking, Client, RoomCategory
from .forms import ClientForm

# =========================================================================
# 1. READ: Каталог номеров (Доступен ВСЕМ, включает поиск и фильтрацию)
# =========================================================================
def room_list(request):
    query = request.GET.get('q', '')
    max_price = request.GET.get('max_price', '')
    category_id = request.GET.get('category', '') # Фильтрация по категориям комфортности БГУИР
    
    rooms = Room.objects.all()
    categories = RoomCategory.objects.all()
    
    # Применение фильтров
    if query:
        rooms = rooms.filter(Q(description__icontains=query) | Q(number__icontains=query))
    if max_price:
        rooms = rooms.filter(price__lte=max_price)
    if category_id:
        rooms = rooms.filter(category_id=category_id)
        
    # Логика БГУИР: Зарегистрированный User-Клиент видит информацию ТОЛЬКО о своей брони
    user_bookings = None
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            client = Client.objects.get(user=request.user)
            user_bookings = Booking.objects.filter(client=client)
        except Client.DoesNotExist:
            pass
            
    # Подключение внешних публичных API (Курс НБРБ + Случайный факт)
    rate, fact = "Недоступно", "Нет факта"
    try:
        r = requests.get('https://nbrb.by', timeout=2)
        if r.status_code == 200: 
            rate = r.json().get('Cur_OfficialRate')
        f = requests.get('https://jsph.pl', timeout=2)
        if f.status_code == 200: 
            fact = f.json().get('text')
    except: 
        pass

    return render(request, 'hotel/room_list.html', {
        'rooms': rooms, 
        'categories': categories, 
        'query': query, 
        'max_price': max_price, 
        'selected_category': category_id,
        'user_bookings': user_bookings, 
        'usd_rate': rate, 
        'fact': fact
    })

# =========================================================================
# 2. УДАЛЕНИЕ БРОНИРОВАНИЯ (Доступно Администраторам)
# =========================================================================
def delete_booking(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    booking = get_object_or_404(Booking, pk=pk)
    booking.delete()
    return redirect('room_list')

# =========================================================================
# 3. МАТЕМАТИЧЕСКАЯ СТАТИСТИКА И ГРАФИКИ (Доступно Администраторам)
# =========================================================================
def statistics_view(request):
    if not request.user.is_staff:
        raise PermissionDenied
        
    bookings = Booking.objects.all()
    clients = Client.objects.all()
    
    costs = [float(b.total_cost) for b in bookings] if bookings.exists() else []
    ages = [c.age for c in clients] if clients.exists() else []
    
    try: 
        mode_val = float(stats.mode(costs, keepdims=True).mode)
    except: 
        mode_val = 0

    stats_data = {
        'income_mean': np.mean(costs) if costs else 0, 
        'income_median': np.median(costs) if costs else 0, 
        'income_mode': mode_val,
        'age_mean': np.mean(ages) if ages else 0, 
        'age_median': np.median(ages) if ages else 0, 
        'total_income': sum(costs)
    }
    
    # Генерация визуализации Matplotlib
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(['Всего броней'], [len(bookings)], color='teal')
    ax.set_ylabel('Количество')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_uri = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return render(request, 'hotel/statistics.html', {'stats': stats_data, 'chart': chart_uri})

# =========================================================================
# 4. СИСТЕМА УПРАВЛЕНИЯ КЛИЕНТАМИ (CRUD - Строго для Администраторов)
# =========================================================================

# READ: Просмотр списка клиентов
def client_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    clients = Client.objects.all()
    return render(request, 'hotel/client_list.html', {'clients': clients})

# CREATE: Создание клиента
def client_create(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'hotel/client_form.html', {'form': form, 'title': 'Добавить клиента'})

# UPDATE: Редактирование клиента
def client_update(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'hotel/client_form.html', {'form': form, 'title': 'Редактировать клиента'})

# DELETE: Удаление клиента
def client_delete(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('client_list')

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register_view(request):
    # Если пользователь уже вошел, ему не нужно регистрироваться
    if request.user.is_authenticated:
        return redirect('room_list')
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически авторизуем пользователя после успешной регистрации
            login(request, user)
            return redirect('room_list')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})
