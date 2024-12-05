from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CategoryMaster, Tag, Collection, BrandMaster, ItemMaster, SubCategoryMaster, InventoryMaster, UnitMaster, ItemImage, MyUser, StockHistory
from django.db.models import Sum
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}



class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = ['email', 'full_name', 'password', 'mobile_number', 'confirmPassword', 'role']
        extra_kwargs = {'email': {'required': True}}

    def validate(self, data):
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError("Passwords do not match")
        if data.get('role') not in dict(MyUser.ROLE_CHOICES):
            raise serializers.ValidationError("Invalid role")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmPassword', None)
        user = MyUser.objects.create_user(**validated_data)
        user.save()
        return user

class StockHistorySerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(source='inventory.item.item_name', read_only=True)

    class Meta:
        model = StockHistory
        fields = [
            'id', 'inventory', 'inventory_item_name', 'previous_quantity', 
            'new_quantity', 'previous_expired_date', 'new_expired_date', 
            'updated_at'
        ]

class CategoryMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryMaster
        fields = '__all__'

class SubCategoryMasterSerializer(serializers.ModelSerializer):
    category = CategoryMasterSerializer()  # Nested serializer to include category details

    class Meta:
        model = SubCategoryMaster
        fields =  '__all__'

class BrandMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandMaster
        fields = '__all__'

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=CategoryMaster.objects.all(), source='sub_category.category')
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategoryMaster.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=BrandMaster.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Include tags
    collections = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), many=True)  # Include collections
    images = ItemImageSerializer(many=True, read_only=True)  # Include images

    class Meta:
        model = ItemMaster
        fields = ['id', 'item_name', 'bar_code', 'category', 'sub_category', 'brand', 'tags', 'collections', 'images', 'created_at', 'updated_at']

class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'slug', 'priority', 'isActive', 'is_public', 'created_at', 'updated_at']

class ItemSerializer(serializers.ModelSerializer):
    sub_category = SubCategoryMasterSerializer()
    brand = BrandMasterSerializer()
    images = ItemImageSerializer(many=True, read_only=True)  # Include images
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Include tags
    collections = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), many=True)  # Include collections
    item_description=serializers.PrimaryKeyRelatedField(queryset=ItemMaster.objects.all())
    status=serializers.PrimaryKeyRelatedField(queryset=ItemMaster.objects.all())
    total_stock = serializers.SerializerMethodField()

    class Meta: 
        model = ItemMaster
        fields = ['id', 'item_name', 'bar_code','item_description','status', 'sub_category', 'brand', 'images', 'tags', 'collections', 'created_at', 'updated_at','total_stock']

    def get_total_stock(self, obj):
        total_stock = InventoryMaster.objects.filter(item=obj).aggregate(total=Sum('unit__quantity'))
        return total_stock['total'] or 0


class UnitMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = ['quantity', 'weight','weight_type']


class InventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    unit = UnitMasterSerializer()

    class Meta:
        model = InventoryMaster
        fields = [
            'id', 'item','selling_price', 'mrp', 'unit', 'pkt_date', 'expired_date', 'is_expired'
        ]