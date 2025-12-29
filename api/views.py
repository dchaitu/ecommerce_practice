from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Brand, Product, Cart, CartItem, Order, OrderItem
from .serializers import BrandSerializer, ProductSerializer, CartSerializer, CartItemSerializer
import razorpay

class BrandListCreate(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class BrandRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price']

    def get_queryset(self):
        queryset = super().get_queryset()
        gender = self.request.query_params.get('gender')
        category = self.request.query_params.get('category')
        brand_name = self.request.query_params.get('brand')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if gender:
            queryset = queryset.filter_by_gender(gender)
        if category:
            queryset = queryset.filter(category=category)
        if brand_name:
            queryset = queryset.filter(brand__name__iexact=brand_name)
        if min_price and max_price:
            queryset = queryset.price_range(min_price, max_price)

        return queryset

class ProductRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # We expect product_id and quantity in request.data
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart, update quantity if so
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                cart_item.quantity = quantity
                cart_item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        # Clear the entire cart
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Calculate amount from user's cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        total_amount = cart.total_value
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create Razorpay Order
        # Amount must be in paise
        amount_in_paise = int(total_amount * 100)
        payment_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_rcptid_{request.user.id}",
            "payment_capture": 1
        }
        
        try:
            razorpay_order = client.order.create(data=payment_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create local Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            razorpay_order_id=razorpay_order['id'],
            is_paid=False
        )

        # Create OrderItems from CartItems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price  # Snapshot the current price
            )
        
        # Return data to frontend
        return Response({
            "order_id": order.razorpay_order_id,
            "amount": amount_in_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
            "name": "Ecommerce Practice",
            "description": "Payment for Cart",
            "prefill": {
                "name": request.user.username,
                "email": request.user.email
            }
        }, status=status.HTTP_201_CREATED)

class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            # Verify signature
            data = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(data)
            
            # Update Order
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.is_paid = True
            order.save()
            
            # Clear Cart (Optional but recommended)
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            
            return Response({"status": "Payment successful"}, status=status.HTTP_200_OK)
            
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)