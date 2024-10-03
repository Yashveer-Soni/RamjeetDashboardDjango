from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ramjeet.views import (
    SignInView, csrf_token, CategoryListView, delete_product, update_product,FetchSingleProduct,
    BrandListView, add_item, SubCategoryListView, ItemMasterListView, 
    ItemMasterDetailView,add_brand,CustomTokenObtainPairView ,search 
)
from django.views.generic import TemplateView




urlpatterns = [
    # path("", TemplateView.as_view(template_name="index.html")),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('csrf/', csrf_token, name='csrf_token'),
    # path('api/current-user/', CurrentUserView.as_view(), name='current-user'),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/brands/', BrandListView.as_view(), name='brand-list'),
    path('api/addbrands/', add_brand, name='add_brand'),
    path('api/subcategories/', SubCategoryListView.as_view(), name='SubCategory-List'),
    path('api/products/', add_item, name='add-product'),
    path('api/search/', search, name='search'),
    path('api/inventory/', ItemMasterListView.as_view(), name='inventory-list'),
    path('api/items/<int:id>/', ItemMasterDetailView.as_view(), name='item-detail'),
    path('api/products/<int:product_id>/', delete_product, name='delete_product'),
    path('api/FetchSingleProduct/<int:product_id>/', FetchSingleProduct, name='FetchSingleProduct'),
    path('api/UpdateProducts/<int:product_id>/', update_product, name='update_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
