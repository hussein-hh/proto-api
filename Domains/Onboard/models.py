from django.db import models
from django.contrib.auth import get_user_model

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

    def __str__(self):
        return self.name

class RoleModelPage(models.Model):
    PAGE_TYPE_CHOICES = [
        ("Landing Page", "Landing Page"),
        ("Search Results Page", "Search Results Page"),
        ("Product Page", "Product Page"),
    ]

    role_model = models.ForeignKey(RoleModel, on_delete=models.CASCADE, related_name="pages")
    page_type = models.CharField(max_length=50, choices=PAGE_TYPE_CHOICES)
    wpm = models.FilePathField(path="uploads", allow_files=True, match=".*\.json$", recursive=True, null=True)
    ui_report = models.FilePathField(path="uploads", allow_files=True, match=".*\.json$", recursive=True, null=True)
    url = models.URLField(null=True, blank=True, max_length=1000)

    def __str__(self):
        return f"{self.role_model.name} - {self.page_type}"


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

    url = models.URLField(null=True, blank=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default="Landing Page")
    business = models.ForeignKey("Business", null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    screenshot = models.TextField(null=True, blank=True)
    html = models.TextField(null=True, blank=True)
    css = models.TextField(null=True, blank=True)
    ui_report = models.TextField(null=True, blank=True)
    wpm = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.page_type} - {self.upload.name} by {self.user.username}"