# Generated by Django 4.2.3 on 2023-07-11 14:14

from django.db import migrations, models
import utils.image_uploaders


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(blank=True, related_name='items_of_cart', to='main.cartitem', verbose_name='Товары'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=utils.image_uploaders.product_image_upload, verbose_name='Изображение товара'),
        ),
    ]
