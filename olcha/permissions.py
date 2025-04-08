from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import timedelta
from django.utils.timezone import now


class IsAdminOrReadOnly(BasePermission):
    """
    Adminlarga barcha metodlar uchun ruxsat, boshqalarga esa faqat read-only metodlar (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsWeekdayOrAdmin(BasePermission):
    """
    Faqat dushanbadan jumagacha comment qo'shish mumkin.
    Adminlarga esa istalgan vaqtda comment qo'shishga ruxsat beriladi.
    """
    def has_permission(self, request, view):
        today = now().weekday()
        if request.user.is_staff:
            return True
        return today in range(5)  # 0=Monday, 4=Friday


class CanDeleteProductInTwoMinutes(BasePermission):
    """
    Faqat 2 daqiqadan oshmagan mahsulotlarni o'chirishga ruxsat beriladi.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return now() - obj.created_at <= timedelta(minutes=2)
        return True