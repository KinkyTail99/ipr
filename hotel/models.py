import re
from datetime import date
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_by_phone(value):
    pattern = r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер телефона должен быть в формате +375 (29) XXX-XX-XX')

def validate_age_18(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Регистрация доступна только для лиц старше 18 лет.')

class RoomCategory(models.Model):
    name = models.CharField('Комфортность (Люкс, Полулюкс, Обычный)', max_length=50)
    def __str__(self): return self.name

class Feature(models.Model):
    name = models.CharField('Дополнительное удобство', max_length=100)
    def __str__(self): return self.name

class Room(models.Model):
    number = models.PositiveIntegerField('Номер комнаты', primary_key=True)
    capacity = models.PositiveIntegerField('Вместимость (кол-во мест)')
    price = models.DecimalField('Цена за сутки (BYN)', max_digits=10, decimal_places=2)
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, verbose_name="Категория")
    features = models.ManyToManyField(Feature, blank=True, verbose_name="Удобства")
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Фото номера', upload_to='rooms/', blank=True, null=True)
    def __str__(self): return f"Номер {self.number} ({self.category.name})"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Аккаунт системы")
    last_name = models.CharField('Фамилия', max_length=50)
    first_name = models.CharField('Имя', max_length=50)
    patronymic = models.CharField('Отчество', max_length=50, blank=True) # Добавлено строго по условию
    phone = models.CharField('Телефон', max_length=20, validators=[validate_by_phone])
    birth_date = models.DateField('Дата рождения', validators=[validate_age_18])
    has_child = models.BooleanField('Есть ли ребенок', default=False) # Добавлено строго по условию
    comment = models.TextField('Комментарий о клиенте', blank=True) # Добавлено строго по условию
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (today.month, today.day))
        
    def __str__(self): return self.full_name

class ClientPassport(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='passport')
    passport_number = models.CharField('Серия и номер паспорта', max_length=20)
    def __str__(self): return f"Паспорт {self.client}"

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Номер")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент", related_name="bookings")
    check_in = models.DateField('Дата поселения (заезд)')
    check_out = models.DateField('Дата освобождения (выезд)')
    total_cost = models.DecimalField('Итоговая цена (Платеж)', max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        delta = self.check_out - self.check_in
        days = max(delta.days, 1)
        self.total_cost = self.room.price * days
        super().save(*args, **kwargs)
        
    def __str__(self): return f"Бронь №{self.id} — {self.client.full_name}"
