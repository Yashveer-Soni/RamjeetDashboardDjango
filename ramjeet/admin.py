from django.contrib import admin
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from .models import (
    Parent_Category, CategoryMaster, SubCategoryMaster, BrandMaster,
    UnitMaster, ItemMaster, InventoryMaster,
    FirmMaster, InverdInventoryMaster, InverdInvoiceProductDetail, ItemImage,CustomerMaster, OrderMaster,OrderItem,PaymentMaster,CouponMaster,StockMovement,UserReviews,SupplierMaster,PurchaseOrderMaster,PurchaseOrderDetail,DeliveryMaster,NotificationMaster,NotificationSettings,ReturnMaster,Wishlist,InventoryAdjustment,ShippingMethod,ShippingDetails, CustomUser,
    Tag,Collection
)

admin.site.site_header = "Ramjeet Dashboard"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Ramjeet"

admin.site.register(CustomUser)
admin.site.register(Tag)
admin.site.register(Collection)
admin.site.register(CustomerMaster)
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
    exclude=('profit','margin','tags','collections','status','is_deleted')
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
class InverdInvoiceProductionDetailAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'invoice', 'item', 'quantity', 'mrp', 'purchase_rate', 'packet_date', 'expired_date', 'unit', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('invoice__invoice_id', 'item__item_name')
    list_filter = ('invoice', 'item', 'is_deleted', 'created_at', 'updated_at')
    actions = ['export_as_csv']
