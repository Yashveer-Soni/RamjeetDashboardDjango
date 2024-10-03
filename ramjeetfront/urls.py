from django.urls import path
from ramjeetfront import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:id>/', views.product_view, name='product_view'),

]
