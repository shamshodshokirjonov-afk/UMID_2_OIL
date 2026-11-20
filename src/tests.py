from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import DailyStats, Fuel


User = get_user_model()


class HomePageTests(TestCase):
    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.get(reverse('home'))

        self.assertRedirects(response, f"{reverse('login')}?next=/")

    def test_authenticated_visitor_sees_home_page(self):
        user = User.objects.create_user(username='haydovchi', password='SafePass!9284')
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Yo‘lingizga')
        self.assertContains(response, 'Yoqilg‘i turlari')
        self.assertContains(response, 'query=Angren+UMID+2+OIL')
        self.assertContains(response, '+998 93 500 06 30')
        self.assertContains(response, '+998 94 313 30 86')
        page = response.content.decode()
        self.assertLess(page.index('AI-92 (O‘zbekiston)'), page.index('AI-92 (Rossiya)'))
        self.assertLess(page.index('AI-92 (Rossiya)'), page.index('AI-95 (Rossiya)'))

    def test_fuel_price_is_shown_when_set_in_admin(self):
        user = User.objects.create_user(username='haydovchi', password='SafePass!9284')
        self.client.force_login(user)
        fuel = Fuel.objects.get(name='AI-92 (O‘zbekiston)')
        fuel.price = '12500'
        fuel.save()

        response = self.client.get(reverse('home'))

        self.assertContains(response, '12\u00a0500')
        self.assertContains(response, 'so‘m/litr')

    def test_daily_stats_table_shows_all_reporting_periods(self):
        user = User.objects.create_user(username='haydovchi', password='SafePass!9284')
        self.client.force_login(user)
        DailyStats.objects.create(
            day=timezone.localdate(),
            vehicles_count=125,
            liters_sold='2345.5',
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Davrlar bo‘yicha ko‘rsatkichlar')
        for period in ('Kunlik', 'Haftalik', 'Oylik', 'Yillik'):
            with self.subTest(period=period):
                self.assertContains(response, period)
        self.assertContains(response, '125')
        self.assertContains(response, '2\u00a0345,50')
        self.assertContains(response, timezone.localdate().strftime('%d.%m.%Y'))
        page = response.content.decode()
        self.assertLess(page.index('id="daily-stats"'), page.index('id="about"'))

    def test_period_totals_use_calendar_boundaries(self):
        user = User.objects.create_user(username='haydovchi', password='SafePass!9284')
        self.client.force_login(user)
        today = timezone.localdate()
        year_start = today.replace(month=1, day=1)
        days = {today - timedelta(days=offset) for offset in range(60)}
        days.add(year_start - timedelta(days=1))
        rows = {}
        for index, day in enumerate(sorted(days), start=1):
            vehicles = index
            liters = index * 10
            rows[day] = (vehicles, liters)
            DailyStats.objects.create(
                day=day,
                vehicles_count=vehicles,
                liters_sold=liters,
            )

        response = self.client.get(reverse('home'))

        week_start = today - timedelta(days=today.weekday())
        period_starts = {
            'Kunlik': today,
            'Haftalik': week_start,
            'Oylik': today.replace(day=1),
            'Yillik': year_start,
        }
        periods = {period['label']: period for period in response.context['stats_periods']}
        for label, start in period_starts.items():
            with self.subTest(period=label):
                included = [values for day, values in rows.items() if start <= day <= today]
                self.assertEqual(periods[label]['vehicles'], sum(row[0] for row in included))
                self.assertEqual(periods[label]['liters'], sum(row[1] for row in included))


class FuelAdminTests(TestCase):
    def test_staff_can_change_fuel_price_in_admin(self):
        admin_user = User.objects.create_superuser(
            username='fueladmin',
            email='admin@example.com',
            password='SafePass!9284',
        )
        fuel = Fuel.objects.get(name='AI-92 (O‘zbekiston)')
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse('admin:src_fuel_change', args=(fuel.pk,)),
            {
                'name': fuel.name,
                'badge': fuel.badge,
                'price': '12500',
                'sort_order': fuel.sort_order,
                '_save': 'Save',
            },
        )

        self.assertEqual(response.status_code, 302)
        fuel.refresh_from_db()
        self.assertEqual(str(fuel.price), '12500.00')

    def test_staff_can_add_daily_stats_in_admin(self):
        admin_user = User.objects.create_superuser(
            username='statsadmin',
            email='stats@example.com',
            password='SafePass!9284',
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse('admin:src_dailystats_add'),
            {
                'day': timezone.localdate().strftime('%Y-%m-%d'),
                'vehicles_count': '125',
                'liters_sold': '2345.5',
                '_save': 'Save',
            },
        )

        self.assertEqual(response.status_code, 302)
        stats = DailyStats.objects.get(day=timezone.localdate())
        self.assertEqual(stats.vehicles_count, 125)
        self.assertEqual(str(stats.liters_sold), '2345.50')

    def test_non_staff_cannot_access_fuel_admin(self):
        user = User.objects.create_user(username='haydovchi', password='SafePass!9284')
        self.client.force_login(user)

        response = self.client.get(reverse('admin:src_fuel_changelist'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response.url)


class AccountFlowTests(TestCase):
    def test_register_creates_account_and_logs_user_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'haydovchi',
            'email': 'driver@example.com',
            'password1': 'SafePass!9284',
            'password2': 'SafePass!9284',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='haydovchi').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(username='first', email='same@example.com', password='SafePass!9284')

        response = self.client.post(reverse('register'), {
            'username': 'second',
            'email': 'SAME@example.com',
            'password1': 'SafePass!9284',
            'password2': 'SafePass!9284',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bu elektron pochta manzili bilan hisob mavjud.')
        self.assertEqual(User.objects.count(), 1)

    def test_login_and_logout(self):
        User.objects.create_user(username='haydovchi', password='SafePass!9284')

        login_response = self.client.post(reverse('login'), {
            'username': 'haydovchi',
            'password': 'SafePass!9284',
        })

        self.assertRedirects(login_response, reverse('home'))
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)

        logout_response = self.client.post(reverse('logout'))

        self.assertRedirects(logout_response, reverse('login'))
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)


class AuthPageTests(TestCase):
    def test_registration_form_includes_email(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Elektron pochta')

    def test_auth_pages_use_root_static_asset_urls(self):
        for url in (reverse('login'), reverse('register')):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'href="/static/css/site.css"')
