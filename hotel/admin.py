from django.contrib import admin
from .models import RoomCategory, Feature, Room, Client, ClientPassport, Booking

# БГУИР: Встроенное редактирование паспорта прямо внутри Клиента (Inline)
class ClientPassportInline(admin.StackedInline):
    model = ClientPassport
    can_delete = False
    verbose_name = "Паспортные данные"
    verbose_name_plural = "Паспортные данные"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'phone', 'birth_date', 'has_child')
    list_filter = ('has_child', 'birth_date') # Фильтрация по ТЗ
    search_fields = ('last_name', 'phone')    # Поиск по ТЗ
    inlines = (ClientPassportInline,)         # Встроенное редактирование по ТЗ

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'capacity', 'price')
    list_filter = ('category', 'capacity')
    search_fields = ('number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'room', 'check_in', 'check_out', 'total_cost')
    list_filter = ('check_in', 'room__category')

admin.site.register(RoomCategory)
admin.site.register(Feature)
