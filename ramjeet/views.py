from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework import generics
from .models import CategoryMaster, BrandMaster, ItemMaster, SubCategoryMaster, InventoryMaster,UnitMaster, Tag, Collection
from .serializers import CategoryMasterSerializer, BrandMasterSerializer, ProductSerializer, CategoryMaster,SubCategoryMasterSerializer, InventorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import redirect
from functools import wraps
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.middleware.csrf import get_token


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

# @ensure_csrf_cookie
# def csrf_token(request):
#     return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE', '')})

def csrf_token(request):
    csrf_token = get_token(request)
    print("csrf_token", csrf_token)
    return JsonResponse({'csrfToken': csrf_token})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role  # Include the role in the token
        token['is_staff'] = user.is_staff  # Include is_staff in the token
        token['is_superuser'] = user.is_superuser  # Include is_superuser in the token

        # Add additional user information to the token
        token['username'] = user.username 
        token['first_name'] = user.first_name  
        token['last_name'] = user.last_name 
        token['email'] = user.email  

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add additional fields to the response
        data['role'] = self.user.role  # Include the role in the response
        data['is_staff'] = self.user.is_staff  # Include is_staff in the response
        data['is_superuser'] = self.user.is_superuser  # Include is_superuser in the response

        # Allow both staff and regular users to log in
        if not self.user.is_active:
            raise serializers.ValidationError('This account is inactive.')

        # Optionally, restrict login based on roles if needed
        if hasattr(self.user, 'role') and self.user.role not in ['admin', 'user']:
            raise serializers.ValidationError('You do not have the required role to log in.')

        return data

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
        
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def CurrentUserView(request):
#     user = request.user
#     serializer = UserSerializer(user)
#     return Response(serializer.data)
    
    
@api_view(['POST'])
def add_item(request):
    data = request.data
    print("data", data)
    files = request.FILES.getlist('images')

    # Check if required keys are in the request data
    required_keys = ['sub_category', 'category', 'brand', 'item_name', 'bar_code', 'mrp', 'purchase_rate', 'pkt_date', 'quantity', 'weight']
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

    # Check for duplicate bar_code
    if ItemMaster.objects.filter(bar_code=data['bar_code']).exists():
        return Response({"error": "Product with this bar_code already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the UnitMaster instance directly
    unit = UnitMaster.objects.create(
        quantity=data['quantity'],
        weight=data['weight'],
        weight_type=data.get('weight_type', 'kg')
    )

    # Create the ItemMaster instance
    item = ItemMaster.objects.create(
        sub_category=sub_category,
        item_name=data['item_name'],
        item_description=data.get('item_description', ''),
        status=data.get('status', 'Draft'),
        cost_per_item=data.get('cost_per_item', 0),
        profit=data.get('profit', 0),
        margin=data.get('margin', 0),
        brand=brand,
        bar_code=data.get('bar_code', ''),
        is_deleted=False
    )

    # Set tags ManyToMany field
    if 'tags' in data:
        tag_names = [name.strip() for name in data['tags'].split(',')]
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]  # Create if not exist
        item.tags.set(tags)

    # Set collections ManyToMany field
    if 'collections' in data:
        collections_names = [name.strip() for name in data['collections'].split(',')]
        collections = [Collection.objects.get_or_create(name=name)[0] for name in collections_names]  # Create if not exist
        item.collections.set(collections)


    # Create the InventoryMaster instance
    inventory_item = InventoryMaster.objects.create(
        item=item,
        mrp=data['mrp'],
        purchase_rate=data['purchase_rate'],
        pkt_date=data['pkt_date'],
        expired_date=data.get('expiry_date'),
        is_expired=data.get('is_expired', False),
        unit=unit 
    )

    # Save images related to the item
    for file in files:
        item.images.create(image=file)

    serializer = ProductSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class ItemMasterListView(generics.ListAPIView):
    queryset = InventoryMaster.objects.all()
    serializer_class = InventorySerializer
    pagination_class = CustomPagination

class ItemMasterDetailView(generics.RetrieveAPIView):
    queryset = ItemMaster.objects.filter(is_deleted=False)  # Adjust the filter as needed
    serializer_class = ProductSerializer
    lookup_field = 'id'  # Use 'id' or the primary key field name if different

@api_view(['GET'])
def test_auth(request):
    permission_classes = [IsAuthenticated]
    return Response(data={"message": "You are authenticated"}, status=200)

@api_view(['DELETE'])
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
def update_product(request, product_id):
    try:
        # Retrieve the product to be updated
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
    product.item_name = data.get('item_name', product.item_name)
    product.sub_category = sub_category
    product.brand = brand
    product.save()

    # Update the InventoryMaster instance
    try:
        inventory_item = InventoryMaster.objects.get(item=product)
        inventory_item.mrp = data.get('mrp', inventory_item.mrp)
        inventory_item.purchase_rate = data.get('purchase_rate', inventory_item.purchase_rate)
        inventory_item.pkt_date = data.get('pkt_date', inventory_item.pkt_date)
        inventory_item.expired_date = data.get('expiry_date', inventory_item.expired_date)
        inventory_item.is_expired = data.get('is_expired', inventory_item.is_expired)
        inventory_item.unit.quantity = data.get('quantity', inventory_item.unit.quantity)
        inventory_item.unit.weight = data.get('weight', inventory_item.unit.weight)
        inventory_item.unit.save()
        inventory_item.save()
    except InventoryMaster.DoesNotExist:
        return Response({"error": "Inventory details not found for the product."}, status=status.HTTP_404_NOT_FOUND)

    # Save images related to the product
    for file in files:
        product.images.create(image=file)

    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_brand(request):
    name = request.data.get('name')
    if BrandMaster.objects.filter(brand_name=name).exists():
        return Response({'error': 'Brand already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = BrandMasterSerializer(data={'brand_name': name})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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