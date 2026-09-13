from django.urls import path
from . import views

urlpatterns = [
    # Storefront & Catalog
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shop/<slug:slug>/review/', views.add_review, name='add_review'),

    # Shopping Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmed/<str:order_number>/', views.order_success, name='order_success'),
    path('track-order/', views.track_order, name='track_order'),

    # Brand Pages
    path('our-story/', views.our_story, name='our_story'),
]
