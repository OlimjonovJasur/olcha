from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from olcha import views


router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubCategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-images', views.ProductImageViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # Avtomatik URL'lar:
    path('', include(router.urls)),

    # Commentlar uchun URL'lar:
    path('comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/by-product/<int:pk>/', views.CommentListCreateView.as_view(), name='comment-list-create-by-product'),

    # Authentication URL'lar:
    path('auth/register/', views.RegisterView.as_view(), name='auth_register'),
    path('auth/login/', views.LoginView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    path('auth/me/', views.UserDetailView.as_view(), name='user_detail'),
]