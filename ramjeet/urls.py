from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ramjeet.views import (
    SignInView,DeliveryAddressListCreateAPIView,DeliveryAddressDetailAPIView, csrf_token,remove_from_cart,StockHistoryListView, CategoryListView, delete_product, update_product,FetchSingleProduct,
    BrandListView,ShippingMethodAPIView, add_item, SubCategoryListView, ItemMasterListView, CurrentUserView,updateStock,MyOrders,
    ItemMasterDetailView,add_brand,CustomTokenObtainPairView ,search,delete_brands,ItemSingleView,validate_token,add_to_cart,get_cart,PlaceOrderAPIView,ClearCartAPIView
)
from django.views.generic import TemplateView




urlpatterns = [
    # path("", TemplateView.as_view(template_name="index.html")),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/validate_token/', validate_token, name='validate_token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('csrf/', csrf_token, name='csrf_token'),
    path('api/current-user/', CurrentUserView, name='current-user'),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/brands/', BrandListView.as_view(), name='brand-list'),
    path('api/addbrands/', add_brand, name='add_brand'),
    path('api/delete_brands/', delete_brands, name='delete_brands'),
    path('api/subcategories/', SubCategoryListView.as_view(), name='SubCategory-List'),
    path('api/products/', add_item, name='add-product'),
    path('api/search/', search, name='search'),
    path('api/inventory/', ItemMasterListView.as_view(), name='inventory-list'),
    path('api/inventory/stockhistory/', StockHistoryListView.as_view(), name='StockHistoryListView'),
    path('api/updateStock/<int:id>/', updateStock, name='updateStock'),
    path('api/inventory/<int:id>/', ItemSingleView.as_view(), name='ItemSingleView'),
    path('api/items/<int:id>/', ItemMasterDetailView.as_view(), name='item-detail'),
    path('api/products/<int:product_id>/', delete_product, name='delete_product'),
    path('api/FetchSingleProduct/<int:product_id>/', FetchSingleProduct, name='FetchSingleProduct'),
    path('api/UpdateProducts/<int:product_id>/', update_product, name='update_product'),
    path('api/AddToCart/', add_to_cart, name='add_to_cart'),
    path('api/RemoveFromCart/', remove_from_cart, name='remove_from_cart'),
    path('api/GetCart/', get_cart, name='update_product'),
    path('api/ClearCart/', ClearCartAPIView.as_view(), name='ClearCartAPIView'),
    path('api/PlaceOrder/', PlaceOrderAPIView.as_view(), name='place_order'),
    path('api/MyOrders/', MyOrders.as_view(), name='MyOrders'),
    path('api/delivery-addresses/', DeliveryAddressListCreateAPIView.as_view(), name='delivery-address-list-create'),
    path('api/delivery-addresses/<int:pk>/', DeliveryAddressDetailAPIView.as_view(), name='delivery-address-detail'),
    path('api/shipping-methods/', ShippingMethodAPIView.as_view(), name='ShippingMethod'),


    # path('api/validate-quantity/<int:product_id>/', validate_quantity, name='validate_quantity'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)