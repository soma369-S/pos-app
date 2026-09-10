from django.core.management.base import BaseCommand
from inventory.models import Brand, Category, MobileProduct


class Command(BaseCommand):
    help = "Seed the catalog with sample brands, categories, and mobile products for demo purposes."

    def handle(self, *args, **options):
        category, _ = Category.objects.get_or_create(name="Smartphone")

        catalog = [
            ("Apple", "iPhone 15", "6GB", "128GB", "Black", 69999, 15),
            ("Apple", "iPhone 15 Pro", "8GB", "256GB", "Titanium Blue", 129999, 8),
            ("Samsung", "Galaxy S24", "8GB", "128GB", "Onyx Black", 74999, 20),
            ("Samsung", "Galaxy A55", "8GB", "128GB", "Awesome Navy", 34999, 25),
            ("OnePlus", "OnePlus 12", "12GB", "256GB", "Flowy Emerald", 64999, 12),
            ("Xiaomi", "Redmi Note 13 Pro", "8GB", "256GB", "Midnight Black", 24999, 30),
            ("Google", "Pixel 8", "8GB", "128GB", "Obsidian", 59999, 10),
            ("Vivo", "V29", "8GB", "128GB", "Space Black", 32999, 18),
        ]

        created = 0
        for brand_name, model_name, ram, storage, color, price, stock in catalog:
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            _, was_created = MobileProduct.objects.get_or_create(
                brand=brand,
                model_name=model_name,
                ram=ram,
                storage=storage,
                defaults={
                    "category": category,
                    "color": color,
                    "price": price,
                    "stock_quantity": stock,
                    "description": f"{model_name} with {ram} RAM and {storage} storage.",
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. {created} new product(s) created."))
