from django.contrib import admin
from .models import Category, SubCategory, Product, ProductImage, Comment, Order


# ProductImage inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# SubCategory inline
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


# Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'image', 'get_subcategories_count')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SubCategoryInline]

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    get_subcategories_count.short_description = 'Subkategoriyalar soni'


# Product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'subcategory', 'category', 'discount')
    list_filter = ('subcategory__category', 'subcategory', 'discount')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

    def save_model(self, request, obj, form, change):
        # Agar category tanlangan bo'lsa va subcategory tanlanmagan bo'lsa
        if obj.category and not obj.subcategory:
            # Birinchi subcategory ni olish
            first_subcategory = SubCategory.objects.filter(category=obj.category).first()
            if first_subcategory:
                obj.subcategory = first_subcategory

        # Agar subcategory tanlangan bo'lsa, uning categorysi bilan product categorysi bir xil emasligini tekshirish
        if obj.subcategory and obj.category and obj.subcategory.category != obj.category:
            # Yangi categoryga tegishli birinchi subcategory ni olish
            first_subcategory = SubCategory.objects.filter(category=obj.category).first()
            if first_subcategory:
                obj.subcategory = first_subcategory

        super().save_model(request, obj, form, change)


# ProductImage admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text')
    search_fields = ('product__name',)
    list_filter = ('product__subcategory',)


# SubCategory admin
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name', 'category__title')
    prepopulated_fields = {'slug': ('name',)}


# Comment admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('message', 'user__username', 'product__name')
    readonly_fields = ('created',)


# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'phone', 'product__name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')