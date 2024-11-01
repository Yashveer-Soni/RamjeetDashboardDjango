from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.http import HttpResponse
from django.template.loader import render_to_string 
from xhtml2pdf import pisa
from io import BytesIO
import csv
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import GroupAdmin
from decimal import Decimal
from .models import (
    Parent_Category, CategoryMaster, SubCategoryMaster, BrandMaster,
    UnitMaster, ItemMaster, InventoryMaster,StockHistory,
    FirmMaster, InverdInventoryMaster, InverdInvoiceProductDetail, ItemImage,CustomerMaster, OrderMaster,OrderItem,PaymentMaster,CouponMaster,StockMovement,UserReviews,SupplierMaster,PurchaseOrderMaster,PurchaseOrderDetail,DeliveryMaster,NotificationMaster,NotificationSettings,ReturnMaster,Wishlist,InventoryAdjustment,ShippingMethod,ShippingDetails,
    Tag,Collection, MyUser
)
admin.site.site_header = "Ramjeet Dashboard"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Ramjeet"

admin.site.register(Tag)
admin.site.register(Collection)
admin.site.register(CustomerMaster)
admin.site.register(StockHistory)
admin.site.register(OrderMaster)
admin.site.register(OrderItem)
admin.site.register(PaymentMaster)
admin.site.register(CouponMaster)
admin.site.register(StockMovement)
admin.site.register(UserReviews)
admin.site.register(SupplierMaster)
admin.site.register(PurchaseOrderMaster)
admin.site.register(PurchaseOrderDetail)
admin.site.register(NotificationMaster)
admin.site.register(NotificationSettings)
admin.site.register(ReturnMaster)
admin.site.register(DeliveryMaster)
admin.site.register(InventoryAdjustment)
admin.site.register(ShippingMethod)
admin.site.register(ShippingDetails)
admin.site.register(Wishlist)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'full_name', 'role')  # Include role in creation form

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'full_name', 'is_active', 'is_admin', 'role', 'is_staff','is_superuser', 'groups')

    def clean_password(self):
        # Return the initial password, regardless of what the user enters
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model
    list_display = ('email', 'full_name', 'is_admin', 'is_staff', 'is_active', 'role', 'is_superuser')  # added is_staff and is_active
    list_filter = ('is_admin', 'is_active', 'role', 'is_superuser', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff' , 'role', 'is_superuser', 'groups')}),  # added is_active, is_admin, and role
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_active', 'is_admin', 'role', 'groups'),  # added is_active, is_admin, and role
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups',) 

# Register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(Parent_Category)
class CategoryParentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'parent_cat_name', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('category_parent',)
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(CategoryMaster)
class CategoryMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'category_name', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('category_name',)
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(SubCategoryMaster)
class SubCategoryMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'category', 'sub_category_name', 'is_expirable', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('sub_category_name',)
    list_filter = ('category', 'is_expirable', 'is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(BrandMaster)
class BrandMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'brand_name', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('brand_name',)
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(UnitMaster)
class UnitMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'quantity', 'weight', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('quantity', 'weight')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1  # Number of empty forms to display initially

@admin.register(ItemMaster)
class ItemMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('item_name', 'brand', 'sub_category', 'image_preview', 'created_at', 'updated_at')
    search_fields = ('item_name', 'brand__brand_name', 'sub_category__sub_category_name')
    list_filter = ('brand', 'sub_category__category__category_name')
    readonly_fields = ('image_preview',)
    actions = ['mark_as_deleted']
    inlines = [ItemImageInline]  # Include ItemImageInline for managing images
    # exclude=('profit','margin','tags','collections','status','is_deleted')
    def mark_as_deleted(self, request, queryset):
        queryset.update(is_deleted=True)

    mark_as_deleted.short_description = "Mark selected items as deleted"

    def image_preview(self, obj):
        if obj.images.exists():
            images = obj.images.all()
            return mark_safe(
                ' '.join(
                    f'<img src="{image.image.url}" width="100px" height="auto" />' for image in images
                )
            )
        else:
            return '(No images)'

    image_preview.short_description = 'Image Preview'

@admin.register(InventoryMaster)
class InventoryMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'mrp', 'purchase_rate', 'pkt_date', 'expired_date', 'is_expired', 'unit', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('item__item_name', 'mrp')
    list_filter = ('is_expired', 'is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        
        expiring_items = InventoryMaster.objects.filter(
            expired_date__lte=timezone.now() + timezone.timedelta(days=5),
            expired_date__gte=timezone.now()
        )
        
        expiring_count = expiring_items.count()
        if expiring_count > 0:
            if expiring_count == 1:
                item = expiring_items.first()
                messages.warning(request, f'Item "{item.item}" is expiring soon on {item.expired_date}!')
            else:
                item_list = ', '.join([item.item.item_name for item in expiring_items[:5]])
                if expiring_count > 5:
                    item_list += ' and more...'
                messages.warning(request, f'There are {expiring_count} items expiring soon within the next 5 days: {item_list}')
        
        return response

@admin.register(FirmMaster)
class FirmMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'firm_name', 'address', 'contact_name', 'phone_number', 'firm_gst_number', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('firm_name', 'contact_name', 'phone_number', 'firm_gst_number')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(InverdInventoryMaster)
class InverdInventoryMasterAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'firm', 'invoice_id', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('invoice_id',)
    list_filter = ('firm', 'is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']

@admin.register(InverdInvoiceProductDetail)
class InverdInvoiceProductDetailAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'invoice', 'item', 'quantity', 'mrp', 'purchase_rate', 'packet_date', 'expired_date', 'unit', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('invoice__invoice_id', 'item__item_name')
    list_filter = ('invoice', 'item', 'is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv', 'generate_invoice_pdf']

    def generate_invoice_pdf(self, request, queryset):
        # Create a buffer to hold the PDF
        buffer = BytesIO()

        # Loop over each selected invoice
        for invoice_detail in queryset:
            # Get the invoice associated with the invoice_detail
            invoice = invoice_detail.invoice

            # Get all the product details related to the invoice
            items = InverdInvoiceProductDetail.objects.filter(invoice=invoice).select_related('item')

            # Prepare a list of items to pass to the template
            invoice_items = []
            subtotal = Decimal('0.00')  # Ensure subtotal is a Decimal
            for item_detail in items:
                item = item_detail.item
                total = item_detail.quantity * item_detail.mrp  # This is valid since both are Decimals
                subtotal += total  # Adding Decimal to Decimal

                # Add item details to the list
                invoice_items.append({
                    'description': item.item_name,
                    'unit_price': item_detail.mrp,
                    'quantity': item_detail.quantity,
                    'total': total,
                })

            # Calculate totals and taxes using Decimals
            tax_rate = Decimal('0.05')  # 5% tax as a Decimal
            tax = subtotal * tax_rate  # Tax is also Decimal
            total = subtotal + tax

            # Prepare context to pass to the template
            context = {
                'invoice': {
                    'client_name': 'Client Name',  # Replace with actual data
                    'client_address': 'Client Address',  # Replace with actual data
                    'invoice_id': invoice.invoice_id,
                    'date': invoice.created_at,
                    'due_date': 'Due Date',  # Replace with actual due date logic
                    'items': invoice_items,
                    'subtotal': subtotal,
                    'tax': tax,
                    'total': total,
                }
            }

            # Render the HTML template with the context
            html_string = render_to_string('ramjeet/invoice_template.html', context)

            # Convert the HTML to PDF
            pisa_status = pisa.CreatePDF(BytesIO(html_string.encode('UTF-8')), dest=buffer)

            if pisa_status.err:
                return HttpResponse('We had some errors with the PDF generation', content_type='text/plain')

        # Prepare HTTP response with the generated PDF
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_id}.pdf'

        return response