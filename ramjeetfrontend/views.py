from django.shortcuts import render, get_object_or_404
from ramjeet.models import ItemMaster

def home_view(request):
    items = ItemMaster.objects.prefetch_related('images', 'inventories').all()
    
    inventory_data = []
    for item in items:
        first_image_url = item.images.all()[0].image.url if item.images.exists() else None
        
        for inventory in item.inventories.all():
            inventory_data.append({
                'id': item.id,
                'item_name': item.item_name,  # Assuming you want to include the item name
                'mrp': float(inventory.mrp),
                'selling_price': float(inventory.selling_price),
                'unit_quantity': inventory.unit.quantity if inventory.unit else None,
                'discount' : (1 - (float(inventory.selling_price) /  float(inventory.mrp))) * 100,
                'stock_status': (
                    "In Stock" if inventory.unit and inventory.unit.quantity > 10 else
                    "Low Quantity" if inventory.unit and inventory.unit.quantity > 0 else
                    "Out of Stock"
                ),
                'image_url': first_image_url  # Add the first image URL to the inventory data
            })
    
    return render(request, 'ramjeetfrontend/index.html', {'items': items, 'inventory_data': inventory_data})



def product_view(request, id):
    # Fetch the product and related inventories and images
    product = ItemMaster.objects.prefetch_related('images', 'inventories__unit').get(id=id)

    # Create a list of inventory data for each inventory's MRP, unit quantity, and stock status
    inventory_data = [
        {   
            'id': product.id,
            'item_name': product.item_name,
            'mrp': float(inventory.mrp),
            'brand':product.brand.brand_name if product.brand else None,
            'selling_price': float(inventory.selling_price),
            'unit_quantity': inventory.unit.quantity if inventory.unit else None,
            'discount' : (1 - (float(inventory.selling_price) /  float(inventory.mrp))) * 100,
            'stock_status': (
                "In Stock" if inventory.unit and inventory.unit.quantity > 10 else
                "Low Quantity" if inventory.unit and inventory.unit.quantity > 0 else
                "Out of Stock"
            )
        }
        for inventory in product.inventories.all()
    ]


    # Fetch all images related to the product
    images = product.images.all()  # Get all related images for the product

    return render(request, 'ramjeetfrontend/product.html', {
        'product': product,
        'inventory_data': inventory_data,
        'images': images,  # Pass images to the template
    })

