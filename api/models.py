from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ProductQuerySet(models.QuerySet):
    def filter_by_gender(self, gender):
        return self.filter(gender=gender)
    
    def price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def filter_by_gender(self, gender):
        return self.get_queryset().filter_by_gender(gender)
    
    def price_range(self, min_price, max_price):
        return self.get_queryset().price_range(min_price, max_price)

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('topwear', 'Top Wear'),
        ('bottomwear', 'Bottom Wear'),
        ('hats', 'Hats'),
        ('footwear', 'Footwear'),
        ('accessories', 'Accessories'),
        ('gadgets', 'Gadgets')
    ]
    
    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Kids', 'Kids'),
        ('Unisex', 'Unisex')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Unisex')
    
    objects = ProductManager()

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_value(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
