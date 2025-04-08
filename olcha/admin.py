# admin.py
from django.contrib import admin
from .models import Category, SubCategory, Product, ProductImage, Comment, Order


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1  # Qo'shimcha bo'sh formalar soni
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'image', 'get_subcategories_count')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SubCategoryInline]

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    get_subcategories_count.short_description = 'Subkategoriyalar soni'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name', 'category__title')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'subcategory', 'discount')
    list_filter = ('subcategory__category', 'subcategory', 'discount')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text')
    search_fields = ('product__name',)
    list_filter = ('product__subcategory',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('message', 'user__username', 'product__name')
    readonly_fields = ('created',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'phone', 'product__name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
