from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # Specify related names to avoid conflicts with auth.Group and auth.Permission
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  
        blank=True,
        help_text=('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  
        blank=True,
        help_text=('Specific permissions for this user.'),
    )
    
class CustomerMaster(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class OrderMaster(models.Model):
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.first_name} {self.customer.last_name}"

class Parent_Category(models.Model):
    parent_cat_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_cat_name

class CategoryMaster(models.Model):
    category_name = models.CharField(max_length=255)
    parent_cat = models.ForeignKey(Parent_Category, on_delete=models.CASCADE)  # Ensure the field name is 'parent_cat'
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

class SubCategoryMaster(models.Model):
    category = models.ForeignKey(CategoryMaster, on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=255)
    is_expirable = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_category_name

class BrandMaster(models.Model):
    brand_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.brand_name
    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Add Brand"

class UnitMaster(models.Model):
    quantity = models.FloatField()
    weight = models.FloatField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} units, {self.weight} weight (kg)"
    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Add Unit"

class ItemMaster(models.Model):
    sub_category = models.ForeignKey(SubCategoryMaster, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    brand = models.ForeignKey(BrandMaster, on_delete=models.CASCADE)
    bar_code = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
    
class OrderItem(models.Model):
    order = models.ForeignKey(OrderMaster, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.item_name} - {self.quantity} pcs"

class PaymentMaster(models.Model):
    order = models.ForeignKey(OrderMaster, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('upi', 'UPI'), ('cash', 'Cash')])
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"

class CouponMaster(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.coupon_code

class StockMovement(models.Model):
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=50, choices=[('in', 'Stock In'), ('out', 'Stock Out')])
    quantity = models.PositiveIntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.item_name} - {self.movement_type}"
    
class UserReviews(models.Model):
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.first_name}'s review of {self.item.item_name}"



class ItemImage(models.Model):
    item = models.ForeignKey(ItemMaster, related_name='images', on_delete=models.CASCADE)  # Establish relationship
    image = models.ImageField(upload_to='product_images/')
    
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Add Item"

class InventoryMaster(models.Model):
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, related_name='inventories')
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2)
    pkt_date = models.DateField()
    expired_date = models.DateField(blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    unit = models.ForeignKey(UnitMaster, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.item.sub_category.is_expirable and self.expired_date is not None:
            raise ValidationError('This product should not have an expiry date.')

    def __str__(self):
        return f"{self.item.item_name} - {self.unit.quantity} units"
    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Add Stock"

class FirmMaster(models.Model):
    firm_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    firm_gst_number = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.firm_name
    class Meta:
        verbose_name = "Firm"
        verbose_name_plural = "Add Firm"

class InverdInventoryMaster(models.Model):
    firm = models.ForeignKey(FirmMaster, on_delete=models.CASCADE)
    invoice_id = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_id

class InverdInvoiceProductDetail(models.Model):
    invoice = models.ForeignKey(InverdInventoryMaster, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2)
    packet_date = models.DateField()
    expired_date = models.DateField()
    unit = models.ForeignKey(UnitMaster, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invoice.invoice_id} - {self.item.item_name}"

class SupplierMaster(models.Model):
    supplier_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.supplier_name

class PurchaseOrderMaster(models.Model):
    supplier = models.ForeignKey(SupplierMaster, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('received', 'Received'), ('cancelled', 'Cancelled')])
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.supplier_name}"

class PurchaseOrderDetail(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrderMaster, on_delete=models.CASCADE, related_name='order_details')
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO #{self.purchase_order.id} - {self.item.item_name}"

class DeliveryMaster(models.Model):
    order = models.ForeignKey(OrderMaster, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    delivery_address = models.CharField(max_length=255)
    delivery_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')])
    delivery_person = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery #{self.id} for Order #{self.order.id}"

class NotificationMaster(models.Model):
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    message = models.TextField()
    notification_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification for {self.customer.first_name} - {self.message[:20]}"
    
class NotificationSettings(models.Model):
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification Settings for {self.customer.first_name}"


class ReturnMaster(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    return_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return #{self.id} for Order Item #{self.order_item.id}"

class Wishlist(models.Model):
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist Item {self.item.item_name} for {self.customer.first_name}"

class InventoryAdjustment(models.Model):
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=50, choices=[('increase', 'Increase'), ('decrease', 'Decrease')])
    quantity = models.PositiveIntegerField()
    reason = models.TextField()
    adjustment_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.adjustment_type.capitalize()} {self.quantity} of {self.item.item_name}"
    
class ShippingMethod(models.Model):
    method_name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_delivery_time = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.method_name

    
class ShippingDetails(models.Model):
    order = models.ForeignKey(OrderMaster, on_delete=models.CASCADE)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    shipping_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipping Details for Order #{self.order.id}"
