from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import RoomCategory, Room, Client, Booking

class HotelComprehensiveTest(TestCase):
    def setUp(self):
        self.category = RoomCategory.objects.create(name="Обычный")
        self.room = Room.objects.create(number=101, capacity=2, price=50.00, category=self.category)
        self.admin_user = User.objects.create_superuser(username='admin_test', password='password123')
        self.regular_user = User.objects.create_user(username='user_test', password='password123')
        self.valid_birth_date = date.today() - timedelta(days=365 * 25)

    def test_room_string_representation(self):
        self.assertEqual(str(self.room), "Номер 101 (Обычный)")

    def test_client_underage_validation_fails(self):
        underage_date = date.today() - timedelta(days=365 * 16)
        client = Client(last_name="Тест", first_name="Тест", phone="+375 (29) 111-22-33", birth_date=underage_date)
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_client_phone_mask_validation_fails(self):
        client = Client(last_name="Тест", first_name="Тест", phone="12345", birth_date=self.valid_birth_date)
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_booking_calculation(self):
        client = Client.objects.create(last_name="Тест", first_name="Тест", phone="+375 (29) 111-22-33", birth_date=self.valid_birth_date)
        booking = Booking.objects.create(room=self.room, client=client, check_in=date.today(), check_out=date.today() + timedelta(days=2))
        self.assertEqual(booking.total_cost, 100.00)

    def test_room_list_view(self):
        response = self.client.get(reverse('room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hotel/room_list.html')

    def test_statistics_view_requires_staff(self):
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 403)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_client_list_requires_staff(self):
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 403)

    def test_client_create_requires_staff(self):
        response = self.client.get(reverse('client_create'))
        self.assertEqual(response.status_code, 403)

    # ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ ДОСТИЖЕНИЯ 85%+ ПОКРЫТИЯ
    def test_admin_can_access_crud_and_stats(self):
        self.client.login(username='admin_test', password='password123')
        
        # Проверка страницы списка клиентов
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        
        # Проверка страницы статистики и расчётов
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_delete_booking(self):
        client = Client.objects.create(last_name="Тест", first_name="Тест", phone="+375 (29) 111-22-33", birth_date=self.valid_birth_date)
        booking = Booking.objects.create(room=self.room, client=client, check_in=date.today(), check_out=date.today() + timedelta(days=1))
        
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('delete_booking', args=[booking.id]))
        self.assertEqual(response.status_code, 302) # Редирект после успешного удаления
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())
