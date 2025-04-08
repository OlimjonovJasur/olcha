from rest_framework import viewsets, filters, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from .models import Category, SubCategory, Product, ProductImage, Comment, Order
from .serializers import (
    CategorySerializer, CategoryDetailSerializer, SubCategorySerializer,
    ProductSerializer, ProductDetailSerializer, ProductImageSerializer,
    CommentModelSerializer, RegisterSerializer, UserSerializer, OrderSerializer
)
from .permissions import IsWeekdayOrAdmin, IsAdminOrReadOnly, CanDeleteProductInTwoMinutes
from .pagination import StandardPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    lookup_field = 'pk'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    search_fields = ['title']
    filter_backends = [filters.SearchFilter]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

    def get_queryset(self):
        return Category.objects.all()  # Pagination ishlashi uchun


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all().order_by('id')
    serializer_class = SubCategorySerializer
    lookup_field = 'pk'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']

    def get_queryset(self):
        return SubCategory.objects.all()  # Pagination ishlashi uchun


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    permission_classes = [IsAdminOrReadOnly, CanDeleteProductInTwoMinutes]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subcategory', 'discount']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        # pagination uchun maxsus filterlashni qo'shish mumkin
        return Product.objects.all().order_by('-created_at')  # Pagination ishlashi uchun

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        product = self.get_object()
        user = request.user

        if user in product.likes.all():
            product.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            product.likes.add(user)
            return Response({'status': 'liked'})


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all().order_by('id')
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']


class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsWeekdayOrAdmin]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'user', 'rating']
    search_fields = ['message']

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        if product_id:
            return Comment.objects.filter(product_id=product_id).order_by('-created')
        return Comment.objects.all().order_by('-created')

    def perform_create(self, serializer):
        product_id = self.kwargs.get('pk')
        if product_id:
            serializer.save(user=self.request.user, product_id=product_id)
        else:
            serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product']
    search_fields = ['full_name', 'phone']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        elif user.is_authenticated:
            return Order.objects.filter(user=user).order_by('-created_at')
        return Order.objects.none()


# JWT
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Foydalanuvchi muvaffaqiyatli yaratildi!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        return Response({"error": "Noto'g'ri username yoki parol"}, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token talab qilinadi"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Tizimdan chiqildi"}, status=200)
        except Exception as e:
            return Response({"error": "Noto'g'ri token"}, status=400)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
