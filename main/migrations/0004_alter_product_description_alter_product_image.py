# Generated by Django 5.0.4 on 2024-06-08 08:46

import utils.image_uploaders
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_brand_options_product_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(verbose_name='Описание товара'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(null=True, upload_to=utils.image_uploaders.product_image_upload, verbose_name='Изображение товара'),
        ),
    ]
