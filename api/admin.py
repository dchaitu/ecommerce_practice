from django.contrib import admin
from django.db.models import Q
from api.models import Product, Brand, User, CartItem, Cart
from .models import Order, OrderItem


class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('0-10', 'Under $10'),
            ('11-50', '$11 - $50'),
            ('51-100', '$51 - $100'),
            ('101-', 'Over $100'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-10':
            return queryset.filter(price__range=(0, 10))
        if self.value() == '11-50':
            return queryset.filter(price__range=(11, 50))
        if self.value() == '51-100':
            return queryset.filter(price__range=(51, 100))
        if self.value() == '101-':
            return queryset.filter(price__gte=101)
        return queryset

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'gender', 'price')
    list_filter = ('brand', 'category', 'gender', PriceRangeFilter)
    search_fields = ('name', 'description')
    list_per_page = 25

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value', 'created_at')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')

    def total_price(self, obj):
        return obj.quantity * obj.product.price
    total_price.short_description = 'Total Price'

admin.site.register(Product, ProductAdmin)
admin.site.register(Brand)
admin.site.register(User)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)