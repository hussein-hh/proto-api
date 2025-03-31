from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RoleModel(models.Model):
    CATEGORY_CHOICES = [
        ("Online Retail & Marketplace", "Online Retail & Marketplace"),
        ("Fashion & Apparel", "Fashion & Apparel"),
        ("Cosmetics & Beauty", "Cosmetics & Beauty"),
        ("Electronics & Gadgets", "Electronics & Gadgets"),
        ("Food & Grocery", "Food & Grocery"),
        ("Toys & Baby Products", "Toys & Baby Products"),
        ("Furniture & Home Decor", "Furniture & Home Decor"),
        ("Jewelry & Accessories", "Jewelry & Accessories"),
        ("Luxury Goods", "Luxury Goods"),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    landing_page = models.URLField(null=True, blank=True)
    results_page = models.URLField(null=True, blank=True)
    product_page = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Business(models.Model):
    CATEGORY_CHOICES = RoleModel.CATEGORY_CHOICES  

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    role_model = models.ForeignKey("RoleModel", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    
class Page(models.Model):
    PAGE_TYPE_CHOICES = [
        ("Landing Page", "Landing Page"),
        ("Search Results Page", "Search Results Page"),
        ("Product Page", "Product Page"),
    ]
    FILE_TYPES = (
        ('txt', 'Text File'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
    )

    path = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.page_type} - {self.upload.name} by {self.user.username}"

class Page(models.Model):
    PAGE_TYPE_CHOICES = [
        ("Landing Page", "Landing Page"),
        ("Search Results Page", "Search Results Page"),
        ("Product Page", "Product Page"),
    ]

    FILE_TYPES = (
        ('txt', 'Text File'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
    )

    name = models.CharField(max_length=255, default="Unnamed File")
    path = models.CharField(max_length=255, default="/default/path/to/file")
    type = models.CharField(max_length=10, choices=FILE_TYPES, default='pdf')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    page_type = models.CharField(max_length=50, choices=PAGE_TYPE_CHOICES, default="Landing Page")

    def __str__(self):
        return f"{self.page_type} - {self.name} by {self.uploaded_by.username}"