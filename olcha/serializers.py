from decimal import Decimal
from rest_framework import serializers
from .models import Category, SubCategory, Product, ProductImage, Comment, Order
from django.contrib.auth.models import User


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']


class ProductSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    likes = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    def get_likes(self, instance):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user in instance.likes.all()

    def get_like_count(self, instance):
        return instance.likes.count()

    def get_discounted_price(self, instance):
        if instance.discount > 0:
            return round(instance.price * (Decimal(1) - instance.discount / Decimal(100)), 2)
        return instance.price

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "discounted_price",
            "discount", "quantity", "likes", "like_count",
            "subcategory_name", "images", "created_at", "updated_at", "slug"
        ]


class ProductDetailSerializer(ProductSerializer):
    category_name = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()
    subcategory_id = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    def get_category_name(self, obj):
        if obj.subcategory and obj.subcategory.category:
            return obj.subcategory.category.title
        return None

    def get_category_id(self, obj):
        if obj.subcategory and obj.subcategory.category:
            return obj.subcategory.category.id
        return None

    def get_subcategory_id(self, obj):
        if obj.subcategory:
            return obj.subcategory.id
        return None

    def get_comments(self, obj):
        comments = obj.comment_product.all().order_by('-created')[:5]   # Faqat so'nggi 5 ta commentni qaytarish
        return CommentModelSerializer(comments, many=True, context=self.context).data

    def get_average_rating(self, obj):
        comments = obj.comment_product.all()
        if not comments:
            return 0
        total = sum(comment.rating for comment in comments)
        return round(total / comments.count(), 1)

    def get_comment_count(self, obj):
        return obj.comment_product.count()

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "discounted_price",
            "discount", "quantity", "likes", "like_count",
            "subcategory_name", "subcategory_id", "category_name", "category_id",
            "images", "created_at", "updated_at", "slug",
            "comments", "average_rating", "comment_count"
        ]


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = SubCategory
        fields = ["id", "name", "category", "category_name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    class Meta:
        model = Category
        fields = ["id", "title", "image", "slug", "subcategories_count"]


class CategoryDetailSerializer(CategorySerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image", "slug", "subcategories_count", "subcategories"]


class CommentModelSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'message', 'user', 'user_name', 'product', 'created', 'image', 'rating']
        read_only_fields = ['user', 'created']


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'product', 'product_name', 'full_name',
            'phone', 'address', 'quantity', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_price', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Foydalanuvchi autentifikatsiya qilingan bo'lsa, uni buyurtmaga qo'shamiz
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['user'] = user

        try:
            return Order.objects.create(**validated_data)
        except ValueError as e:
            raise serializers.ValidationError({"error": str(e)})


# Authentication serializer'lar
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Parollar bir xil emas."})

        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Bu email allaqachon ro'yxatdan o'tgan."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')