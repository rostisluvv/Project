from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Category

class ProductTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            unit_price=10.00,
            quantity=100,
            category=self.category,
            image="test.jpg"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")

# Create your tests here.
