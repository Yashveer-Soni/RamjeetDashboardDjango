from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class MyUserManager(BaseUserManager):
    def create_user(self, email, full_name,role, password=None):
       
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth, and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            full_name=full_name,
        )
        user.is_admin = True
        user.is_staff = True  # Set staff status
        user.is_superuser = True  # Set superuser status
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin): 
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name =  models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Add this field as Boolean
    is_superuser = models.BooleanField(default=False)  # Add this field as Boolean

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return self.is_superuser or super().has_module_perms(app_label)
    
        
class CustomerMaster(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='customer_profile')
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
    

class DeliveryAddress(models.Model):
    customer = models.ForeignKey(CustomerMaster, related_name="delivery_addresses", on_delete=models.CASCADE)
    full_name=models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True) 
    phoneNumber= models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False) 
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.country}"

    class Meta:
        verbose_name = "Delivery Address"
        verbose_name_plural = "Delivery Addresses"

class OrderMaster(models.Model):
    customer = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    # status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')])
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
    weight_type=models.CharField(max_length=50, choices=[('kg', 'Kg'), ('g', 'G'), ('l', 'L'), ('ml', 'Ml'), ('pcs', 'Pcs')], null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} units, {self.weight} weight ({self.weight_type})"
    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Add Unit"

class Tag(models.Model):
    name =models.CharField(blank=True, null=True)

    def __str__(self):
        return self.name

class Collection(models.Model):
    name =models.CharField(blank=True, null=True)

    def __str__(self):
        return self.name



class ItemMaster(models.Model):
    sub_category = models.ForeignKey(SubCategoryMaster, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    item_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('draft', 'Draft')], default='draft')
    tags = models.ManyToManyField(Tag, blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    brand = models.ForeignKey(BrandMaster, on_delete=models.SET_NULL, null=True, blank=True)
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
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margin = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pkt_date = models.DateField()
    expired_date = models.DateField(blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    unit = models.ForeignKey(UnitMaster, on_delete=models.CASCADE, blank=True, null=True)
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

class StockHistory(models.Model):
    inventory = models.ForeignKey(InventoryMaster, on_delete=models.CASCADE)
    previous_quantity = models.IntegerField(null=True, blank=True)
    new_quantity = models.IntegerField(null=True, blank=True)
    previous_expired_date = models.DateField(null=True, blank=True)
    new_expired_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update on {self.updated_at} for {self.inventory.item.item_name}"

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
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    shipping_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipping Details for Order #{self.shipping_method.id}"

class DeliveryMaster(models.Model):
    order = models.ForeignKey(OrderMaster, on_delete=models.CASCADE)
    shipping_detail=models.ForeignKey(ShippingDetails,on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE)
    delivery_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'),('canceled','Canceled')])
    delivery_person = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    canceled_at = models.DateTimeField(null=True, blank=True)
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
    

    

class Cart(models.Model):
    user = models.ForeignKey(CustomerMaster, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.email}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('InventoryMaster', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.item.item_name} - {self.quantity}"

    def get_total_price(self):
        return self.quantity * self.product.selling_price