from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CategoryMaster, BrandMaster, ItemMaster, SubCategoryMaster, InventoryMaster, UnitMaster, ItemImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

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
    images = ItemImageSerializer(many=True, read_only=True)  # Include images

    class Meta:
        model = ItemMaster
        fields = ['id', 'item_name', 'bar_code', 'category', 'sub_category', 'brand', 'images', 'created_at', 'updated_at']

class ItemSerializer(serializers.ModelSerializer):
    sub_category = SubCategoryMasterSerializer()
    brand = BrandMasterSerializer()
    images = ItemImageSerializer(many=True, read_only=True)  # Include images

    class Meta:
        model = ItemMaster
        fields = ['id','item_name', 'bar_code', 'sub_category', 'brand', 'images', 'created_at', 'updated_at']

class UnitMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMaster
        fields = ['quantity', 'weight']

class InventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    unit = UnitMasterSerializer()

    class Meta:
        model = InventoryMaster
        fields = ['id','item', 'mrp','purchase_rate', 'unit', 'pkt_date', 'expired_date', 'is_expired']