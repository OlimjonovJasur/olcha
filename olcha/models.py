from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Category(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    slug = models.SlugField(null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='products', blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='products')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Comment(models.Model):
    class RatingChoices(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comment_product')
    created = models.DateTimeField(auto_now_add=True)
    image = models.FileField(upload_to='comments', null=True, blank=True)
    rating = models.IntegerField(choices=RatingChoices)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=255)
    phone = PhoneNumberField(region='UZ')
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Agar yangi buyurtma bo'lsa va mahsulot yetarli bo'lsa
        if not self.pk and self.product.quantity >= self.quantity:
            # Chegirmali narxni hisoblaymiz
            if self.product.discount > 0:
                price = self.product.price * (1 - self.product.discount / 100)
            else:
                price = self.product.price

            self.total_price = price * self.quantity

            # Mahsulot miqdorini kamaytiramiz
            self.product.quantity -= self.quantity
            self.product.save(update_fields=["quantity"])

            super().save(*args, **kwargs)
        # Agar mavjud buyurtma yangilanayotgan bo'lsa
        elif self.pk:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Yetarli mahsulot mavjud emas!")

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"