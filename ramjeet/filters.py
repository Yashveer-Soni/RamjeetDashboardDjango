import django_filters
from .models import ItemMaster, InventoryMaster

class ItemMasterFilter(django_filters.FilterSet):
    class Meta:
        model = ItemMaster
        fields = {
            'item_name': ['icontains'],
            'brand__brand_name': ['exact'],
            'sub_category__category__category_name': ['exact'],
            # Add more fields as needed
        }

class InventoryMasterFilter(django_filters.FilterSet):
    class Meta:
        model = InventoryMaster
        fields = {
            'item__item_name': ['icontains'],
            'mrp': ['gte', 'lte'],
            'purchase_rate': ['gte', 'lte'],
            'pkt_date': ['exact', 'range'],
            'expired_date': ['exact', 'range'],
            'unit__quantity': ['exact', 'gte', 'lte'],
        }
