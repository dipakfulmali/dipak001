from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [    
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  # Updated to use user_login
    path('logout/', views.logout_view, name='logout'), 
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase_quantity/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('cart/', views.cart, name='cart'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('upload_profile_photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/remove/<int:user_id>/', views.admin_remove_user, name='admin_remove_user'),
    path('admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/products/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('api/payment/', views.process_payment, name='process_payment'),
    path('payment_options/<int:product_id>/', views.payment_options, name='payment_options'),
    path('add_card/', views.add_card, name='add_card'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



