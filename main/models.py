from django.conf import settings
from django.db import models
from django.db.models import Max
from django.urls import reverse

from utils.image_uploaders import product_image_upload
from utils.help_funcs import convert_to_rubles_to_html


class Category(models.Model):

    name = models.CharField("Название", max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"{self.name} | {self.id}"

    def get_absolute_url(self):
        return reverse('category', kwargs={'pk': self.pk})

    def get_brands_sorted(self):
        return self.brand_set.all().order_by('name')


class Brand(models.Model):

    name = models.CharField("Название бренда", max_length=100)
    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория")

    class Meta:
        unique_together = ("name", "category")
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return f"{self.name} | Катeгория - {self.category.name}"


class Product(models.Model):

    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категории", related_name="products")
    brand = models.ForeignKey(Brand, models.CASCADE, verbose_name="Бренд", related_name="brand_products")
    slug = models.SlugField(unique=True)
    title = models.CharField("Название товара", max_length=255)
    description = models.TextField("Описание товара")
    image = models.ImageField("Изображение товара", upload_to=product_image_upload, null=True)
    price = models.DecimalField("Цена товара", max_digits=9, decimal_places=2, default=0)


    class Meta:
        unique_together = ("category", "title", "slug")
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return " - ".join([self.title, self.category.name])

    def get_absolute_url(self):
        return reverse('product', kwargs={'pk': self.pk})

    def get_price(self):
        return convert_to_rubles_to_html(self.price)


class Customer(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField("Номер телефона", max_length=20, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self):
        return f"Покупатель - {self.user.email}"


class Cart(models.Model):

    owner = models.ForeignKey(Customer, models.CASCADE, verbose_name="Владелец")
    items = models.ManyToManyField("CartItem", verbose_name="Товары", related_name="items_of_cart", blank=True)
    total_cost = models.DecimalField("Общая стоимость корзины", decimal_places=2, max_digits=9, default=0)
    in_order = models.BooleanField(default=False, verbose_name="В заказе")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина покупателя - {self.owner.user.email}"

    def add(self, product, qty=1):
        products_in_cart = [item.product for item in self.items.all()]
        if product not in products_in_cart:
            new_cart_item = CartItem.objects.create(
                cart=self,
                product=product,
                qty=qty,
                total_cost=product.price * qty
            )
            self.items.add(new_cart_item)

    def remove(self, item):
        if item in self.items.all():
            self.items.remove(item)
            item.delete()

    def change_item_qty(self, item, qty):
        if item in self.items.all():
            item.qty = qty
            item.total_cost = item.product.price * qty
            item.save()

    def get_cart_items(self):
        return ((item.product, item) for item in self.items.all().annotate(Max('created_at')).order_by('-created_at'))

    def get_total_cost(self):
        return convert_to_rubles_to_html(self.total_cost)


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, models.CASCADE, verbose_name="Корзина", related_name="cart_items")
    product = models.ForeignKey(Product, models.CASCADE, verbose_name="Товар")
    qty = models.IntegerField("Кол-во товара", default=1)
    total_cost = models.DecimalField("Общая стоимость", decimal_places=2, max_digits=9)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар корзины"
        verbose_name_plural = "Товары корзин"

    def __str__(self):
        return " | ".join([f"{self.id}", f"{self.product.title}", f"Корзина={self.cart.id}"])

    def get_total_cost(self):
        return convert_to_rubles_to_html(self.total_cost)


class Order(models.Model):
    
    NEW = "new"
    IN_PROGRESS = "in_progress"
    IS_READY = "ready"
    COMPLETED = "completed"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    
    STATUS_CHOICES = (
        (NEW, "Новый"),
        (IN_PROGRESS, "В обработке"),
        (IS_READY, "Готов"),
        (COMPLETED, "Завершен"),
        (ON_THE_WAY, "В пути"),
        (DELIVERED, "Доставлен"),
    )
    
    BUYING_TYPE_SELF = "self"
    BUYING_TYPE_DELIVERY = "delivery"
    
    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, "Самовывоз"),
        (BUYING_TYPE_DELIVERY, "Доставка")
    )
    
    customer = models.ForeignKey(Customer, models.CASCADE, verbose_name="Покупатель")
    cart = models.ForeignKey(Cart, models.CASCADE, verbose_name="Корзина")
    status = models.CharField("Статус заказа", max_length=20, choices=STATUS_CHOICES, default=NEW)
    comment = models.TextField("Комментарий к заказу", blank=True)
    order_cost = models.DecimalField("Стоимость заказа", max_digits=9, decimal_places=2)
    order_date = models.DateField("Дата заказа", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания заказа", auto_now_add=True)
    buying_type = models.CharField("Тип заказа", max_length=20, choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    phone = models.CharField("Номер телефона", max_length=20)
    first_name = models.CharField("Имя", max_length=255)
    last_name = models.CharField("Фамилия", max_length=255)
    address = models.CharField("Адрес", max_length=1024, null=True, blank=True)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def __str__(self):
        return f"Заказ №{self.id} | Покупатель={self.customer.user.email}"

    def get_order_cost(self):
        return convert_to_rubles_to_html(self.order_cost)
