from django.contrib import admin

from .models import DailyStats, Fuel


@admin.register(Fuel)
class FuelAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge', 'price', 'sort_order')
    list_editable = ('price',)
    ordering = ('sort_order', 'pk')
    search_fields = ('name',)


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('day', 'vehicles_count', 'liters_sold')
    list_editable = ('vehicles_count', 'liters_sold')
    date_hierarchy = 'day'
    ordering = ('-day',)
