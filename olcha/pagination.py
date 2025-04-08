from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Standart pagination - har bir sahifada 20 ta element
    """
    page_size = 20  # Standart sahifa hajmi
    page_size_query_param = 'page_size'  # Sahifa hajmini o'zgartirish uchun parametr
    max_page_size = 1000  # Maksimal sahifa hajmi

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })