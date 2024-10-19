from django.shortcuts import render, get_object_or_404
from ramjeet.models import ItemMaster,OrderItem,InventoryMaster, InventoryAdjustment
from django.db.models import Sum, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_inventory_data(item):
    inventory_data = {}
    first_image_url = item.images.first().image.url if item.images.exists() else None

    total_purchased_stock_query = InventoryMaster.objects.filter(item=item, is_deleted=False)
    total_purchased_stock = total_purchased_stock_query.aggregate(
        total_quantity=Sum(F('unit__quantity'))
    )['total_quantity'] or 0


    # Total sold stock
    # we need change
    # total_sold_stock_query = OrderItem.objects.filter(item=item, is_deleted=True)
    # total_sold_stock = total_sold_stock_query.aggregate(Sum('quantity'))['quantity__sum'] or 0
    # print(f"Total Sold Stock: {total_sold_stock}")

    total_sold_stock_query = InventoryAdjustment.objects.filter(item=item, is_deleted=False)
    total_sold_stock = total_sold_stock_query.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Calculate current stock
    current_stock = int(total_purchased_stock - total_sold_stock)

    for inventory in item.inventories.all():
        item_id = item.id
        if item_id not in inventory_data:
            total_discount = (1 - (float(inventory.selling_price) / float(inventory.mrp))) * 100 if inventory.mrp else 0

            if current_stock <= 0:
               stock_status = "Out of Stock"
            elif current_stock <= 5:
                stock_status = f"Hurry up ! Only {current_stock} product{'s' if current_stock > 1 else ''} remaining"
            else:
                stock_status = "In Stock"
            inventory_data[item_id] = {
                'id': item.id,
                'item_name': item.item_name,
                'description': item.item_description if hasattr(item, 'item_description') else None,
                'mrp': float(inventory.mrp) if inventory.mrp else None,
                'brand': item.brand.brand_name if item.brand else None,
                'selling_price': float(inventory.selling_price) if inventory.selling_price else None,
                'unit_quantity': total_purchased_stock,  # Total purchased quantity
                'current_stock': current_stock,  # Current stock after sales
                'sold_stock': total_sold_stock,  # Total sold stock
                'discount': total_discount,
                'stock_status': stock_status,
                'image_url': first_image_url  # First image URL if available
            }
        # else:
        #     # If you need to update quantities, for example, if you're summing stock:
        #     inventory_data[item_id]['unit_quantity'] += total_purchased_stock
        #     inventory_data[item_id]['current_stock'] += current_stock
        #     inventory_data[item_id]['sold_stock'] += total_sold_stock

    # Convert the dictionary back to a list
    inventory_list = list(inventory_data.values())

    return inventory_list




def home_view(request):
    items = ItemMaster.objects.prefetch_related('images', 'inventories').all()
    
    # Create a paginator object with 10 items per page
    paginator = Paginator(items, 30)
    
    page_number = request.GET.get('page')  # Get the page number from the query parameters
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If the page is not an integer, return the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), return the last page
        page_obj = paginator.page(paginator.num_pages)

    inventory_data = []
    for item in page_obj:
        inventory_data.extend(get_inventory_data(item))
    
    return render(request, 'ramjeetfrontend/index.html', {
        'items': page_obj,  # Pass the paginated items
        'inventory_data': inventory_data,
    })


def product_view(request, id):
    product = get_object_or_404(ItemMaster.objects.prefetch_related('images', 'inventories__unit'), id=id)

    inventory_data = get_inventory_data(product)

    images = product.images.all() 

    return render(request, 'ramjeetfrontend/product.html', {
        'product': product,
        'inventory_data': inventory_data,
        'images': images, 
    })


def contact_us(request):
    return render(request, 'ramjeetfrontend/contact.html')


def shop(request):
    items = ItemMaster.objects.prefetch_related('images', 'inventories').all()
    
    # Create a paginator object with 10 items per page
    paginator = Paginator(items, 30)

    page_number = request.GET.get('page')  # Get the page number from the query parameters
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If the page is not an integer, return the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), return the last page
        page_obj = paginator.page(paginator.num_pages)

    inventory_data = []
    for item in page_obj:
        inventory_data.extend(get_inventory_data(item))
    
    return render(request, 'ramjeetfrontend/collection.html', {
        'items': page_obj,  # Pass the paginated items
        'inventory_data': inventory_data,
    })
