from django.db import models
from django.contrib.auth import get_user_model
import os
import uuid

class Business(models.Model):
    CATEGORY_CHOICES = [
        ("Online Retail", "Online Retail (General E-commerce)"),
        ("Fashion & Apparel", "Fashion & Apparel"),
        ("Cosmetics & Beauty", "Cosmetics & Beauty"),
        ("Electronics & Gadgets", "Electronics & Gadgets"),
        ("Home & Furniture", "Home & Furniture"),
        ("Food & Grocery", "Food & Grocery"),
        ("Health & Wellness", "Health & Wellness"),
        ("Luxury Goods", "Luxury Goods"),
        ("Automotive & Auto Parts", "Automotive & Auto Parts"),
        ("Books & Stationery", "Books & Stationery"),
        ("Sports & Outdoor Gear", "Sports & Outdoor Gear"),
        ("Toys & Baby Products", "Toys & Baby Products"),
        ("Pet Supplies", "Pet Supplies"),
        ("Subscription Services", "Subscription Services"),
        ("Digital Products & Services", "Digital Products & Services"),
        ("Event Ticketing", "Event Ticketing"),
        ("Furniture & Home Decor", "Furniture & Home Decor"),
        ("Jewelry & Accessories", "Jewelry & Accessories"),
        ("Pharmaceutical & Medical Supplies", "Pharmaceutical & Medical Supplies"),
        ("Fast Fashion & Budget Shopping", "Fast Fashion & Budget Shopping"),
    ]
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    url = models.URLField(unique=True)
    role_model = models.URLField(unique=False,null=True)
    goal = models.FileField(upload_to="business/goals/", null=True, blank=True)

    def __str__(self):
        return self.name