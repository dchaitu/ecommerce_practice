from django.core.management.base import BaseCommand
from api.models import Brand, Product
import random

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        brands = ['Nike', 'Adidas', 'Puma', 'Reebok', 'Under Armour']
        for brand_name in brands:
            Brand.objects.get_or_create(name=brand_name)

        categories = [
            'topwear', 'bottomwear', 'hats', 'footwear', 'accessories', 'gadgets'
        ]
        
        genders = ['Men', 'Women', 'Kids', 'Unisex']

        products_data = [
            ('T-Shirt', 'Comfortable cotton t-shirt', 20.00),
            ('Jeans', 'Classic blue jeans', 50.00),
            ('Sneakers', 'Running shoes', 80.00),
            ('Cap', 'Baseball cap', 15.00),
            ('Watch', 'Digital watch', 100.00),
            ('Socks', 'Cotton socks', 5.00),
        ]

        for i in range(50):
            name_base, desc_base, price_base = random.choice(products_data)
            brand = Brand.objects.order_by('?').first()
            category = random.choice(categories)
            gender = random.choice(genders)
            
            Product.objects.create(
                name=f"{brand.name} {name_base} {i}",
                description=f"{desc_base} for {gender}",
                price=price_base + random.randint(0, 10),
                brand=brand,
                category=category,
                gender=gender
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
