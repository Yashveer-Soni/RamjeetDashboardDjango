from django.urls import path
from ramjeetfrontend import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:id>/', views.product_view, name='product_view'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('shop/', views.shop, name='shop'),
]
