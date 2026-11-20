from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Fuel(models.Model):
    name = models.CharField(max_length=100, verbose_name='Yoqilg‘i nomi')
    badge = models.CharField(max_length=10, verbose_name='Belgisi')
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Narxi (so‘m/litr)',
    )
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')

    class Meta:
        ordering = ('sort_order', 'pk')
        verbose_name = 'yoqilg‘i'
        verbose_name_plural = 'yoqilg‘ilar'

    def __str__(self):
        return self.name


class DailyStats(models.Model):
    day = models.DateField(default=timezone.localdate, unique=True, verbose_name='Sana')
    vehicles_count = models.PositiveIntegerField(verbose_name='Kelgan avtomobillar soni')
    liters_sold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Sotilgan yoqilg‘i (litr)',
    )

    class Meta:
        ordering = ('-day',)
        verbose_name = 'kunlik ko‘rsatkich'
        verbose_name_plural = 'kunlik ko‘rsatkichlar'

    def __str__(self):
        return self.day.isoformat()
