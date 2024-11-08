from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CategoryMaster, Tag, Collection, BrandMaster, ItemMaster, SubCategoryMaster, InventoryMaster, UnitMaster, ItemImage, MyUser, StockHistory
from django.db.models import Sum
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

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
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True) 
    collections = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), many=True) 
    images = ItemImageSerializer(many=True, read_only=True)  # Include images

    class Meta:
        model = ItemMaster
        fields = ['id', 'item_name', 'bar_code', 'category', 'sub_category', 'brand', 'tags', 'collections', 'images', 'created_at', 'updated_at']



class ItemSerializer(serializers.ModelSerializer):
    sub_category = SubCategoryMasterSerializer()
    brand = BrandMasterSerializer()
    images = ItemImageSerializer(many=True, read_only=True)  # Include images
    tags =  serializers.StringRelatedField(many=True) 
    collections = serializers.StringRelatedField(many=True) 
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

    purchase_rate = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = InventoryMaster
        fields = [
            'id', 'item', 'selling_price', 'mrp', 'unit', 'pkt_date', 'expired_date', 'is_expired', 'purchase_rate'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        request = self.context.get('request', None)
        if request and not request.user.is_staff:
            representation['purchase_rate'] = '****'  
        
        return representation


