from django.db import migrations, models


def create_fuels(apps, schema_editor):
    Fuel = apps.get_model('src', 'Fuel')
    fuels = (
        ('AI-92 (O‘zbekiston)', '92', 1),
        ('AI-92 (Rossiya)', '92', 2),
        ('AI-95 (Rossiya)', '95', 3),
        ('Dizel yoqilg‘isi', 'D', 4),
        ('Propan', 'G', 5),
    )
    Fuel.objects.using(schema_editor.connection.alias).bulk_create([
        Fuel(name=name, badge=badge, sort_order=order)
        for name, badge, order in fuels
    ])


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Fuel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Yoqilg‘i nomi')),
                ('badge', models.CharField(max_length=10, verbose_name='Belgisi')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Narxi (so‘m/litr)')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')),
            ],
            options={
                'verbose_name': 'yoqilg‘i',
                'verbose_name_plural': 'yoqilg‘ilar',
                'ordering': ('sort_order', 'pk'),
            },
        ),
        migrations.RunPython(create_fuels, migrations.RunPython.noop),
    ]
