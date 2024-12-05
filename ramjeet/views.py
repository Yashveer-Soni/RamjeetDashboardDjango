from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
import uuid
from django.db import transaction
import json
import base64
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from django.core.files.base import ContentFile
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
from rest_framework import generics
from .models import CategoryMaster,ShippingMethod,DeliveryMaster,ShippingDetails,CustomerMaster, DeliveryAddress,BrandMaster,ItemImage,MyUser, ItemMaster, SubCategoryMaster, InventoryMaster,UnitMaster, Tag, Collection,StockHistory,Cart, CartItem, OrderMaster, OrderItem
from .serializers import CollectionSerializer,SignUpSerializer,CustomerProfileSerializer,ItemImageSerializer,DeliveryAddressSerializer,CategoryMasterSerializer,StockHistorySerializer, BrandMasterSerializer, ProductSerializer, CategoryMaster,SubCategoryMasterSerializer, InventorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import redirect,get_object_or_404
from functools import wraps
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.middleware.csrf import get_token
from django.db.models import Sum
from twilio.rest import Client
import random

# from django.db.models import Q

# user_email = request.user.email
# user_mobile = request.user.phone_number  # Assuming phone_number is available on request.user

# # Construct query conditions
# query = Q(is_deleted=False)
# if user_email:
#     query &= Q(customer__email=user_email)
# if user_mobile:
#     query |= Q(customer__phone_number=user_mobile)

# # Apply the query to the filter method
# order = OrderMaster.objects.filter(Q(id=order_id) & query).first()

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_sms_via_twilio(phone_number, otp):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP code is {otp}",
        from_='+1234567890',  # Your Twilio phone number
        to=phone_number  # The phone number to which OTP will be sent
    )

    return message.sid

def generate_unique_tracking_number():
    tracking_number = str(uuid.uuid4()) 
    
    while ShippingDetails.objects.filter(tracking_number=tracking_number).exists():
        tracking_number = str(uuid.uuid4()) 
    
    return tracking_number

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if hasattr(request.user, 'role') and request.user.role == required_role:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('permission_denied')  # Redirect to a 'permission denied' page
            else:
                return redirect('login')
        return _wrapped_view
    return decorator

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_collection(request):
    data = request.data
    product_ids = [product['id'] for product in data.get('products', [])]

    # Validate required fields
    required_keys = ['name', 'slug']
    for key in required_keys:
        if key not in data:
            return Response({"error": f"'{key}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a collection with the same name already exists
    if Collection.objects.filter(name=data['name']).exists():
        return Response({"error": "A collection with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create collection
    collection = Collection.objects.create(
        name=data['name'],
        description=data.get('description', ''),  # Optional description
        slug=data['slug'],
        priority=1,
        isActive=data.get('isActive', True),
        is_public=data.get('is_public', True),
    )
    # Associate products using the set() method
    collection.products.set(product_ids)

    # Serialize and return response
    serializer = CollectionSerializer(collection)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_collection(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    
    # Update fields
    collection.name = data.get('name', collection.name)
    collection.description = data.get('description', collection.description)
    collection.slug = data.get('slug', collection.slug)
    collection.priority = data.get('priority', collection.priority)
    collection.isActive = data.get('isActive', collection.isActive)
    collection.is_public = data.get('is_public', collection.is_public)

    collection.save()

    # Serialize and return response
    serializer = CollectionSerializer(collection)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_collection(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)

    # Perform a hard delete from the database
    collection.delete()

    return Response({"message": "Collection deleted successfully."}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    try:
        token = request.headers.get('Authorization').split()[1]
        decoded_token = AccessToken(token)  
        print(decoded_token)

        user = request.user
        if hasattr(user, 'role'):
            data = {
                "user": user.email,
                "role": user.role,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "User role attribute not found"}, status=status.HTTP_403_FORBIDDEN
            )

    except Exception as e:
        print(f"Token validation error: {e}")
        return Response(
            {"detail": "Invalid token or expired"}, status=status.HTTP_401_UNAUTHORIZED
        )

def csrf_token(request):
    csrf_token = get_token(request)
    print("csrf_token", csrf_token)
    return JsonResponse({'csrfToken': csrf_token})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.role 
        token['is_staff'] = user.is_staff 
        token['is_superuser'] = user.is_superuser 

        token['full_name'] = user.full_name  
        token['email'] = user.email  

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['role'] = self.user.role 
        data['is_staff'] = self.user.is_staff 
        data['is_superuser'] = self.user.is_superuser 

        if not self.user.is_active:
            raise serializers.ValidationError('This account is inactive.')

        if hasattr(self.user, 'role') and self.user.role not in ['admin', 'user']:
            raise serializers.ValidationError('You do not have the required role to log in.')

        return data
    

@api_view(['POST'])
def signup(request):
    phone_number = request.data.get('phone_number', '')

    # Validate phone number
    if not phone_number:
        return Response({"message": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if phone number starts with '+' and prepend '+91' if not
    if not phone_number.startswith('+'):
        phone_number = '+91' + phone_number

    # Generate OTP
    mobile_otp = generate_otp()
    otp_expiration_time = timezone.now() + timedelta(minutes=2)  # OTP validity 2 minutes

    try:
        # Check if user already exists or not
        user = MyUser.objects.get(phone_number=phone_number)
        user.mobile_otp = mobile_otp
        user.otp_created_at = otp_expiration_time
        user.save()
    except MyUser.DoesNotExist:
        # Create new user if not exists
        user = MyUser.objects.create(
            phone_number=phone_number,
            otp=mobile_otp,
            otp_created_at=otp_expiration_time,
            is_active=False,
        )

    # Send OTP via Twilio (dummy function `send_sms_via_twilio`)
    message_status = send_sms_via_twilio(phone_number, mobile_otp)
    if not message_status:
        return Response(
            {"message": "Failed to send OTP. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({
        "message": "OTP sent to the mobile number. Please verify the OTP."
    })


@api_view(['POST'])
def verify_otp(request):
    phone_number = request.data.get('phone_number', '')
    otp = request.data.get('otp', '')

    if not phone_number or not otp:
        return Response({"message": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = MyUser.objects.get(phone_number=phone_number)

        # Validate OTP
        if user.mobile_otp != otp:
            return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is expired
        if user.otp_created_at < timezone.now():
            return Response({"message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Activate the user
        user.is_active = True
        user.mobile_otp = None  # Clear OTP after successful verification
        user.save()

        has_profile = CustomerMaster.objects.filter(user=user).exists()
        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "OTP verified successfully.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "has_profile": has_profile
        })

    except MyUser.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def create_customer_profile(request):
    phone_number = request.data.get('phone_number', '')

    if not phone_number:
        return Response({"message": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the user based on the phone number
        user = MyUser.objects.get(phone_number=phone_number)

        # Ensure the user is active
        if not user.is_active:
            return Response({"message": "User is not active. Please verify OTP first."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the customer profile already exists
        if CustomerMaster.objects.filter(user=user).exists():
            return Response({"message": "Customer profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the customer profile
        full_name = request.data.get('full_name', '')
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        customer = CustomerMaster.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=request.data.get('email', ''),  # Optional: Save email if provided
            phone_number=phone_number,
            address=request.data.get('address', ''),
        )
        customer.save()

        return Response({"message": "Customer profile created successfully."})

    except MyUser.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    if request.user.is_authenticated:
        user = request.user

    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity'))

    product = get_object_or_404(InventoryMaster, id=product_id)

    if product.unit.quantity < quantity:
        return JsonResponse({
            'success': False,
            'message': f'Only {product.unit.quantity} items are available in stock.'
        }, status=400)

    customer = CustomerMaster.objects.get(email=request.user.email)

    cart, created = Cart.objects.get_or_create(user=customer)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        # Update the cart item with the exact quantity (not incrementing)
        cart_item.quantity = quantity
    else:
        # If it's a new cart item, set the quantity directly
        cart_item.quantity = quantity

    cart_item.save()

    return JsonResponse({
        'success': True,
        'message': 'Item added to cart successfully!',
        'cart_item_id': cart_item.id,
        'total_price': cart_item.get_total_price(),
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    if request.user.is_authenticated:
        user = request.user

    product_id = request.data.get('product_id')
    product = get_object_or_404(InventoryMaster, id=product_id)
    customer = CustomerMaster.objects.get(email=request.user.email)
    cart, created = Cart.objects.get_or_create(user=customer)
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()  
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart successfully!'
        })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found in cart!'
        }, status=400)

         # {
        #     "method_name": "Free Shipping",
        #     "cost": Decimal("0.00"),  # Free shipping, no cost
        #     "estimated_delivery_time": "2 hour",
        #     "is_active": True
        # },
        # {
        #     "method_name": "Standard Shipping",
        #     "cost": Decimal("10.00"),  # Cost for standard shipping
        #     "estimated_delivery_time": "5 hour",
        #     "is_active": True
        # },
        # {
        #     "method_name": "Express Shipping",
        #     "cost": Decimal("20.00"),  # Cost for express shipping
        #     "estimated_delivery_time": "1 hour",
        #     "is_active": True
        # },
        
        # if Decimal(total_amount) > 500: 
        #     shipping_method = ShippingMethod.objects.get(method_name="Free Shipping")
        # else:
@permission_classes([IsAuthenticated])
class PlaceOrderAPIView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        cart_items = request.data.get('cart_items')
        total_amount = request.data.get('total_amount')
        deliveryAddressId = request.data.get('deliveryAdderess_id')
        shippingMethod = request.data.get('shippingMethod')

        # Fetch customer and delivery address
        try:
            customer = CustomerMaster.objects.get(email=customer_id)
            delivery_address = DeliveryAddress.objects.get(id=deliveryAddressId)
        except (CustomerMaster.DoesNotExist, DeliveryAddress.DoesNotExist):
            return Response({'error': 'Invalid customer or delivery address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock availability for all items in the cart
        insufficient_stock_items = []
        for item in cart_items:
            try:
                product = ItemMaster.objects.get(id=item['id'])
                inventory_item = InventoryMaster.objects.get(item=product)

                if inventory_item.is_deleted:
                    insufficient_stock_items.append({
                        'item_name': product.item_name,
                        'error': 'Item is no longer available.'
                    })
                elif inventory_item.unit.quantity < item['quantity']:
                    insufficient_stock_items.append({
                        'item_name': product.item_name,
                        'error': f'Not enough stock. Available quantity: {inventory_item.unit.quantity}'
                    })
            except (ItemMaster.DoesNotExist, InventoryMaster.DoesNotExist):
                return Response({'error': f'Invalid item with ID {item["id"]} in cart.'}, status=status.HTTP_400_BAD_REQUEST)

        # If there are insufficient stock items, return an error response
        if insufficient_stock_items:
            return Response({
                'error': 'Insufficient stock for some items.',
                'details': insufficient_stock_items
            }, status=status.HTTP_400_BAD_REQUEST)

        # Start a transaction to ensure all changes are atomic
        with transaction.atomic():
            # Create the order
            order = OrderMaster.objects.create(
                customer=customer,
                total_amount=total_amount,
                # status='pending',
                payment_status='unpaid',
            )

            # Add items to the order
            for item in cart_items:
                product = ItemMaster.objects.get(id=item['id'])
                unit_price = Decimal(item['unitPrice'])
                total_price = Decimal(item['price'])

                OrderItem.objects.create(
                    order=order,
                    item=product,
                    quantity=item['quantity'],
                    unit_price=unit_price,
                    total_price=total_price
                )

                # Reduce the stock quantity
                inventory_item = InventoryMaster.objects.get(item=product)
                inventory_item.unit.quantity -= item['quantity']
                inventory_item.unit.save()

            # Handle shipping details and delivery
            shipping_method = ShippingMethod.objects.filter(method_name=shippingMethod).first()
            tracking_number = generate_unique_tracking_number()
            shipping_details = ShippingDetails.objects.create(
                shipping_method=shipping_method,
                tracking_number=tracking_number,
                shipping_date=None,
                delivery_date=None
            )

            DeliveryMaster.objects.create(
                order=order,
                shipping_detail=shipping_details,
                delivery_address=delivery_address,
                delivery_status='pending',  # Initial status
                delivery_person='Not Assigned',  # Can be updated later
                contact_number='Not Available',  # Can be updated later
            )

        # Return success response
        return Response({'message': 'Order placed successfully!'}, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated]) 
class ShippingMethodAPIView(APIView):
    def get(self, request):
        try:
            shipping_methods = ShippingMethod.objects.all()
            shipping_method_data = [
                {
                    "id":method.id,
                    "method_name": method.method_name,
                    "cost": str(method.cost), 
                    "estimated_delivery_time": method.estimated_delivery_time,
                    "is_active": method.is_active
                }
                for method in shipping_methods
            ]

            return Response({"shipping_methods": shipping_method_data}, status=status.HTTP_200_OK)

        except ShippingMethod.DoesNotExist:
            return Response({"detail": "No shipping methods found."}, status=status.HTTP_404_NOT_FOUND)
    
@permission_classes([IsAuthenticated])
class ClearCartAPIView(APIView):
    def post(self, request):
        customer_id = request.user.email
        try:
            cart_items = Cart.objects.filter(user__email=customer_id)
            cart_items.delete()
            return Response({'message': 'Cart cleared successfully!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class CancelOrder(APIView):
    def post(self, request):
        """
        Cancel an order for the authenticated user.
        """ 
        try:
            customer_id = request.user.email
            order_id = request.data.get('order_id')
            if not order_id:
                return Response({'message': 'Order ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            order = OrderMaster.objects.filter(id=order_id, customer__email=customer_id, is_deleted=False).first()
            
            if not order:
                return Response({'message': 'Order not found or does not belong to this user.'}, status=status.HTTP_404_NOT_FOUND)
            
            delivery_info = DeliveryMaster.objects.filter(order=order, is_deleted=False).first()

            if not delivery_info:
                return Response({'message': 'No delivery information found for this order.'}, status=status.HTTP_404_NOT_FOUND)

            if delivery_info.delivery_status in ['delivered', 'shipped']:
                return Response({'message': 'Order cannot be canceled, it is already delivered or shipped.'})

            delivery_info.delivery_status = 'canceled'
            delivery_info.canceled_at=timezone.now()
            delivery_info.save()
            print("Sdf")

            return Response({'message': 'Order successfully canceled.'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@permission_classes([IsAuthenticated])
class MyProfile(APIView):
    def get(self, request):
        """
        Retrieve the authenticated user's profile.
        """
        try:
            customer = CustomerMaster.objects.get(user=request.user, is_deleted=False)
            serializer = CustomerProfileSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerMaster.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """
        Update the authenticated user's profile.
        """
        try:
            customer = CustomerMaster.objects.get(user=request.user, is_deleted=False)
            serializer = CustomerProfileSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomerMaster.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
       

@permission_classes([IsAuthenticated])
class MyOrders(APIView):
    def get(self, request):
        """
        Fetch all orders for the authenticated user, including order items, delivery details, shipping information, and customer data.
        """
        try:
            # Get the customer's email
            customer = request.user.email
            # Filter orders based on the customer
            orders = OrderMaster.objects.filter(customer__email=customer, is_deleted=False).order_by('-created_at')

            if not orders.exists():
                return Response({'message': 'No orders found.'})

            # Prepare serialized response
            orders_data = []
            for order in orders:
                order_items = order.order_items.all()  
                items_data = []
                for item in order_items:
                    item_images = ItemImage.objects.filter(item=item.item)
                    item_image_data=ItemImageSerializer(item_images, many=True).data
                    items_data.append({
                        'item_name': item.item.item_name,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price),
                        'total_price': float(item.total_price),
                        'images': item_image_data,  # Include the list of image URLs
                    })
                # Fetch delivery information
                delivery_info = DeliveryMaster.objects.filter(order=order, is_deleted=False).first()
                if delivery_info:
                    shipping_details = ShippingDetails.objects.get(id=delivery_info.shipping_detail.id)
                    delivery_address = DeliveryAddress.objects.get(id=delivery_info.delivery_address.id)

                    delivery_data = {
                        'delivery_status': delivery_info.delivery_status,
                        'delivery_person': delivery_info.delivery_person,
                        'contact_number': delivery_info.contact_number,
                        'shipping_details': {
                            'shipping_method': shipping_details.shipping_method.method_name,
                            'tracking_number': shipping_details.tracking_number,
                            'shipping_date': shipping_details.shipping_date.strftime('%Y-%m-%d %H:%M:%S') if shipping_details.shipping_date else None,
                            'delivery_date': shipping_details.delivery_date.strftime('%Y-%m-%d %H:%M:%S') if shipping_details.delivery_date else None,
                        },
                        'delivery_address': {
                            'full_name': delivery_address.full_name,
                            'address_line_1': delivery_address.address_line_1,
                            'address_line_2': delivery_address.address_line_2,
                            'phone_number': delivery_address.phoneNumber,
                            'city': delivery_address.city,
                            'state': delivery_address.state,
                            'postal_code': delivery_address.postal_code,
                            'country': delivery_address.country,
                            'is_default': delivery_address.is_default,
                        }
                    }
                else:
                    delivery_data = None

                orders_data.append({
                    'order_id': order.id,
                    'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_amount': float(order.total_amount),
                    'payment_status': order.payment_status,
                    'items': items_data,
                    'delivery_info': delivery_data,
                })


            return Response({'orders': orders_data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    if request.method == 'GET':
        customer = CustomerMaster.objects.get(email=request.user.email)
        cart = get_object_or_404(Cart, user=customer)
        
        cart_items = []
        
        for item in cart.items.all():
            product_image_url = None
            if item.product.item.images.exists():
                product_image_url = f"http://{request.META['HTTP_HOST']}{item.product.item.images.first().image.url}"
            
            cart_items.append({
                'id': item.id,
                'productId':item.product.item.id,
                'product_name': item.product.item.item_name,
                'quantity': item.quantity,
                'unitPrice':item.product.selling_price,
                'price': item.get_total_price(),
                'image': product_image_url,
            })
        
        return JsonResponse({'success': True, 'cart_items': cart_items})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    
# def validate_quantity(request, product_id):
#     if request.method == 'GET':  
#         product = get_object_or_404(InventoryMaster, id=product_id)
#         quantity = int(request.GET.get('quantity', 1000))

#         if quantity > product.unit.quantity:
#             return JsonResponse({
#                 'success': False,
#                 'message': f'Only {product.unit.quantity} items are available in stock.'
#             }, status=400)

#         return JsonResponse({
#             'success': True,
#             'message': 'Quantity is valid.'
#         })

#     return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
    
class SignInView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            print(access_token);
            refresh_token = str(refresh)
            
            print(user.is_staff)
            print(user.is_superuser)

            # Include user role information
            return Response({
                'message': 'Login successful',
                'access': access_token,
                'refresh': refresh_token,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CategoryListView(generics.ListAPIView):
    queryset = CategoryMaster.objects.filter(is_deleted=False)
    serializer_class = CategoryMasterSerializer

class SubCategoryListView(generics.ListAPIView):
    serializer_class = SubCategoryMasterSerializer

    def get_queryset(self):
        queryset = SubCategoryMaster.objects.filter(is_deleted=False)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class BrandListView(generics.ListAPIView):
    queryset = BrandMaster.objects.filter(is_deleted=False)
    serializer_class = BrandMasterSerializer


        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def CurrentUserView(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request):
    data = request.data
    files = request.FILES.getlist('files') 

    required_keys = ['sub_category', 'files','category', 'brand', 'item_name', 'bar_code', 'mrp', 'purchase_rate', 'pkt_date', 'quantity', 'weight']
    for key in required_keys:
        if key not in data:
            return Response({"error": f"'{key}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = CategoryMaster.objects.get(id=data['category'])
    except CategoryMaster.DoesNotExist:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        sub_category = SubCategoryMaster.objects.get(id=data['sub_category'], category=category)
    except SubCategoryMaster.DoesNotExist:
        return Response({"error": "SubCategory not found or does not match the category."}, status=status.HTTP_404_NOT_FOUND)

    try:
        brand = BrandMaster.objects.get(id=data['brand'])
    except BrandMaster.DoesNotExist:
        return Response({"error": "Brand not found."}, status=status.HTTP_404_NOT_FOUND)

    if ItemMaster.objects.filter(bar_code=data['bar_code']).exists():
        return Response({"error": "Product with this bar_code already exists."}, status=status.HTTP_400_BAD_REQUEST)

    unit = UnitMaster.objects.create(
        quantity=data['quantity'],
        weight=data['weight'],
        weight_type=data.get('weightType')
    )
    print(data.get('status'))

    item = ItemMaster.objects.create(
        sub_category=sub_category,
        item_name=data['item_name'],
        item_description=data.get('item_description', ''),
        status=data.get('status').lower() or 'draft',
        brand=brand,
        bar_code=data['bar_code'],
        is_deleted=False
    )

    # Handle tags
    if 'tags' in data:
        tag_names = [name.strip() for name in data['tags'].split(',')]
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]  # Create if not exist
        item.tags.set(tags)

    # Handle collections
    if 'collections' in data:
        collections_names = [name.strip() for name in data['collections'].split(',')]
        collections = [Collection.objects.get_or_create(name=name)[0] for name in collections_names]  # Create if not exist
        item.collections.set(collections)

    # Create Inventory
    inventory_item = InventoryMaster.objects.create(
        item=item,
        mrp=data['mrp'],
        purchase_rate=data['purchase_rate'],
        selling_price=data.get('selling_price', 0),  # Default to 0 if not provided
        cost_per_item=data.get('cost_per_item', 0),
        profit=data.get('profit', 0),
        margin=data.get('margin', 0),
        pkt_date=data['pkt_date'],
        expired_date=data.get('expiry_date'),
        is_expired=data.get('is_expired', False),
        unit=unit 
    )

    for file in files:
        ItemImage.objects.create(item=item, image=file)  

    # Serialize and return response
    serializer = ProductSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

@permission_classes([AllowAny])
class ItemMasterListView(generics.ListAPIView):
    queryset = InventoryMaster.objects.annotate(total_stock=Sum('unit__quantity')).order_by('item')
    serializer_class = InventorySerializer
    pagination_class = CustomPagination

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateStock(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            inventory = get_object_or_404(InventoryMaster, pk=id)

            previous_quantity = inventory.unit.quantity
            previous_expired_date = inventory.expired_date

            if 'expired_date' in data:
                inventory.expired_date = data['expired_date']

            if 'quantity' in data:
                inventory.unit.quantity = data['quantity']
                inventory.unit.save() 

            inventory.save() 

            StockHistory.objects.create(
                inventory=inventory,
                previous_quantity=previous_quantity,
                new_quantity=inventory.unit.quantity,
                previous_expired_date=previous_expired_date,
                new_expired_date=inventory.expired_date,
            )

            return JsonResponse({'message': 'Stock updated successfully', 'data': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
    

class ItemSingleView(APIView):
    def get(self, request, id):
        try:
            product = InventoryMaster.objects.get(pk=id)
            serializer = InventorySerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InventoryMaster.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

class ItemMasterDetailView(generics.RetrieveAPIView):
    queryset = ItemMaster.objects.filter(is_deleted=False)  # Adjust the filter as needed
    serializer_class = ProductSerializer
    lookup_field = 'id'  # Use 'id' or the primary key field name if different

class StockHistoryListView(APIView):
    def get(self, request):
        stock_history = StockHistory.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 20  
        paginated_stock_history = paginator.paginate_queryset(stock_history, request)
        serializer = StockHistorySerializer(paginated_stock_history, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def test_auth(request):
    permission_classes = [IsAuthenticated]
    return Response(data={"message": "You are authenticated"}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, product_id):
    try:
        product = ItemMaster.objects.get(pk=product_id)
        product.delete()
        return Response({"success": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except ItemMaster.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def FetchSingleProduct(request, product_id):
    try:
        item = InventoryMaster.objects.get(pk=product_id)
        serializer = InventorySerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ItemMaster.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    try:
        product = ItemMaster.objects.get(pk=product_id)
    except ItemMaster.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    files = request.FILES.getlist('images')

    # Check if required keys are in the request data
    required_keys = ['item_name', 'mrp', 'purchase_rate', 'weight', 'quantity', 'category', 'sub_category', 'brand', 'expiry_date', 'pkt_date']
    for key in required_keys:
        if key not in data:
            return Response({"error": f"'{key}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and retrieve the CategoryMaster object
    try:
        category = CategoryMaster.objects.get(id=data['category'])
    except CategoryMaster.DoesNotExist:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate and retrieve the SubCategoryMaster object
    try:
        sub_category = SubCategoryMaster.objects.get(id=data['sub_category'], category=category)
    except SubCategoryMaster.DoesNotExist:
        return Response({"error": "SubCategory not found or does not match the category."}, status=status.HTTP_404_NOT_FOUND)

    # Validate and retrieve the BrandMaster object
    try:
        brand = BrandMaster.objects.get(id=data['brand'])
    except BrandMaster.DoesNotExist:
        return Response({"error": "Brand not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the ItemMaster instance
    tags_names = data.get('tags', [])
    tags_list = [tag.strip() for tag in tags_names.split(',')]
    tags = []
    for tag_name in tags_list:
        tag, created = Tag.objects.get_or_create(name=tag_name) 
        tags.append(tag)

    collection_names = data.get('collections', [])
    collection_list = [collection.strip() for collection in collection_names.split(',')]
    collections = []
    for collection_name in collection_list:
        collection, created = Collection.objects.get_or_create(name=collection_name)
        collections.append(collection)

    product.item_name = data.get('item_name', product.item_name)
    product.item_description = data.get('item_description', product.item_description)
    product.status = data.get('status', product.status)
    product.tags.set(tags)
    product.collections.set(collections)
    product.sub_category = sub_category
    product.brand = brand
    product.save()

    # Update the InventoryMaster instance
    try:
        inventory_item = InventoryMaster.objects.get(item=product)
        inventory_item.mrp = data.get('mrp', inventory_item.mrp)
        inventory_item.purchase_rate = data.get('purchase_rate', inventory_item.purchase_rate)
        inventory_item.cost_per_item = data.get('cost_per_item', inventory_item.cost_per_item)or 0
        inventory_item.selling_price = data.get('selling_price', inventory_item.selling_price)
        inventory_item.pkt_date = data.get('pkt_date', inventory_item.pkt_date)
        inventory_item.expired_date = data.get('expiry_date', inventory_item.expired_date)
        inventory_item.is_expired = data.get('is_expired', inventory_item.is_expired)
        inventory_item.unit.quantity = data.get('quantity', inventory_item.unit.quantity)
        inventory_item.unit.weight = data.get('weight', inventory_item.unit.weight)
        inventory_item.unit.weight_type = data.get('weight_type', inventory_item.unit.weight_type)
        inventory_item.unit.save()
        inventory_item.save()
    except InventoryMaster.DoesNotExist:
        return Response({"error": "Inventory details not found for the product."}, status=status.HTTP_404_NOT_FOUND)
    
    print(files)
    # Save images related to the product
    if 'image' in data and data['image'] is None:
        product.images.all().delete()
    else:
        for file in files:
            product.images.create(image=file)

    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_brand(request):
    name = request.data.get('name')
    print(name)
    if BrandMaster.objects.filter(brand_name=name).exists():
        return Response({'error': 'Brand already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = BrandMasterSerializer(data={'brand_name': name})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_brands(request):
    brand_ids = request.data.get('ids', [])

    if isinstance(brand_ids, list):
        brands_to_delete = BrandMaster.objects.filter(id__in=brand_ids)
    else:
        brands_to_delete = BrandMaster.objects.filter(id=brand_ids)

    if not brands_to_delete.exists():
        return Response({'error': 'No brands found to delete.'}, status=status.HTTP_404_NOT_FOUND)

    count, _ = brands_to_delete.delete()
    return Response({'message': f'{count} brand(s) deleted successfully.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def search(request):
    query = request.GET.get('query', '') 

    if query:
        items = InventoryMaster.objects.filter(
            Q(item__item_name__icontains=query) 
        )
        serializer = InventorySerializer(items[:10], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
class DeliveryAddressListCreateAPIView(APIView):
    """
    Handle GET and POST requests for delivery addresses.
    """
    def get(self, request):
        # Get all delivery addresses
        userId=request.user.email
        delivery_addresses = DeliveryAddress.objects.filter(customer__email=userId,is_deleted=False)
        serializer = DeliveryAddressSerializer(delivery_addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            customer = CustomerMaster.objects.get(user__email=request.user.email)
        except CustomerMaster.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)
        

        request.data['customer'] = customer.id
        request.data['country'] = 'India'

        serializer = DeliveryAddressSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class DeliveryAddressDetailAPIView(APIView):
    """
    Handle GET, PUT, DELETE requests for a single delivery address.
    """
    def get_object(self, pk):
        try:
            return DeliveryAddress.objects.get(pk=pk, is_deleted=False)
        except DeliveryAddress.DoesNotExist:
            return None

    def get(self, request, pk):
        delivery_address = self.get_object(pk)
        if delivery_address is not None:
            serializer = DeliveryAddressSerializer(delivery_address)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        customer = CustomerMaster.objects.get(user__email=request.user.email)
        request.data['customer'] = customer.id
        request.data['country'] = 'India'
        delivery_address = self.get_object(pk)
        if delivery_address is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeliveryAddressSerializer(delivery_address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delivery_address = self.get_object(pk)
        if delivery_address is not None:
            delivery_address.is_deleted = True
            delivery_address.save()
            return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)