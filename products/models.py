from django.db import models
from django.urls import reverse

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Notebooks', 'Notebooks'),
        ('Writing', 'Writing Instruments'),
        ('Bags', 'Bags & Backpacks'),
        ('Art', 'Art Supplies'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Product image file")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    reviews_count = models.IntegerField(default=0)
    is_on_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[str(self.id)])
        
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            from django.db.models import Avg
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg, 2)
            self.reviews_count = reviews.count()
        else:
            self.rating = 0.00
            self.reviews_count = 0
        self.save()

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
