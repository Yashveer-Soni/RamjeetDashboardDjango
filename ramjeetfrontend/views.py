from django.shortcuts import render, get_object_or_404
from ramjeet.models import ItemMaster

def home_view(request):
    # Fetch all items and prefetch related images and inventory data
    items = ItemMaster.objects.prefetch_related('images', 'inventories').all()
    
    # Create a list of inventory data for each item
    inventory_data = []
    for item in items:
        for inventory in item.inventories.all():
            inventory_data.append({
                'item_name': item.item_name,  # Assuming you want to include the item name
                'mrp': float(inventory.mrp),
                'purchase_rate': float(inventory.purchase_rate),
                'unit_quantity': inventory.unit.quantity if inventory.unit else None,
                'stock_status': (
                    "In Stock" if inventory.unit.quantity > 10 else
                    "Low Quantity" if inventory.unit.quantity > 0 else
                    "Out of Stock"
                )
            })
    
    return render(request, 'ramjeetfrontend/index.html', {'items': items, 'inventory_data': inventory_data})


def product_view(request, id):
    # Fetch the product and related inventories
    product = ItemMaster.objects.prefetch_related('images', 'inventories__unit').get(id=id)

    # Create a list of tuples for each inventory's MRP, unit quantity, and stock status
    inventory_data = [
        {
            'mrp': float(inventory.mrp),
            'purchase_rate': float(inventory.purchase_rate),
            'unit_quantity': inventory.unit.quantity if inventory.unit else None,
            'stock_status': (
                "In Stock" if inventory.unit.quantity > 10 else
                "Low Quantity" if inventory.unit.quantity > 0 else
                "Out of Stock"
            )
        }
        for inventory in product.inventories.all()
    ]

    return render(request, 'ramjeetfrontend/product.html', {
        'product': product,
        'inventory_data': inventory_data,
    })


