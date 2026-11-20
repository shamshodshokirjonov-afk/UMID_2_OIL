from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .forms import RegistrationForm
from .models import DailyStats, Fuel


@login_required
def home(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    periods = (
        ('Kunlik', today, today),
        ('Haftalik', week_start, today),
        ('Oylik', month_start, today),
        ('Yillik', year_start, today),
    )
    stats_periods = []
    for label, start, end in periods:
        totals = DailyStats.objects.filter(day__range=(start, end)).aggregate(
            vehicles=Sum('vehicles_count'),
            liters=Sum('liters_sold'),
        )
        stats_periods.append({
            'label': label,
            'date_range': (
                start.strftime('%d.%m.%Y')
                if start == end
                else f'{start:%d.%m.%Y} — {end:%d.%m.%Y}'
            ),
            'vehicles': totals['vehicles'],
            'liters': totals['liters'],
        })

    return render(request, 'home.html', {
        'fuels': Fuel.objects.all(),
        'stats_periods': stats_periods,
    })


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Hisobingiz muvaffaqiyatli yaratildi. Xush kelibsiz!')
        return redirect('home')

    return render(request, 'accounts/register.html', {'form': form})
