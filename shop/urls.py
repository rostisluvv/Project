from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('category/<int:id>/', views.category_products, name='category_products'),
    path('cart/', views.cart, name='cart'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('search/', views.product_search, name='product_search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('create_order/', views.create_order, name='create_order'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('FitLife/', views.FitLife, name='FitLife'),


]
