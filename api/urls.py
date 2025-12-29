from django.urls import path
from .views import (
    BrandListCreate,
    BrandRetrieveUpdateDestroy,
    ProductListCreate,
    ProductRetrieveUpdateDestroy,
    CartView,
    CreateOrderAPIView,
    VerifyPaymentAPIView,
)

urlpatterns = [
    path('brands/', BrandListCreate.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', BrandRetrieveUpdateDestroy.as_view(), name='brand-retrieve-update-destroy'),
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroy.as_view(), name='product-retrieve-update-destroy'),
    path('cart/', CartView.as_view(), name='cart'),
    path('payment-create/', CreateOrderAPIView.as_view(), name='payment-create'),
    path('payment-verify/', VerifyPaymentAPIView.as_view(), name='payment-verify'),
]

