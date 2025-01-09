from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import CustomUser, Product, CartItem
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaymentSerializer
import requests  # Ensure requests is imported
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        
        if CustomUser.objects.filter(username=email).exists():
            return render(request, 'web_app/register.html', {'error_message': 'Email already exists'})
        
        try:
            user = CustomUser.objects.create_user(username=email, password=password, email=email, first_name=first_name, last_name=last_name, phone=phone)
            return redirect('login')  # Redirect to login page after successful registration
        except IntegrityError:
            return render(request, 'web_app/register.html', {'error_message': 'Phone number already exists'})
    return render(request, 'web_app/register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)  # Use auth_login to log in the user
                return redirect('home')
            else:
                return render(request, 'web_app/login.html', {'error_message': 'Invalid email or password'})
        else:
            return render(request, 'web_app/login.html', {'error_message': 'Email and password are required'})
    
    return render(request, 'web_app/login.html')

def home(request):
    products = Product.objects.all()
    context = {
        'user_authenticated': request.user.is_authenticated,
        'products': products,
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/home.html', context)

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@user_passes_test(lambda u: u.is_superuser)
def admin_user_list(request):
    users = CustomUser.objects.all()
    context = {
        'users': users,
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/admin_user_list.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_remove_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()
    return redirect('admin_user_list')

@user_passes_test(lambda u: u.is_superuser)
def admin_add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        description = request.POST['description']
        image = request.FILES['image']
        Product.objects.create(name=name, price=price, description=description, image=image)
        return redirect('home')
    context = {
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/admin_add_product.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.description = request.POST['description']
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        return redirect('home')
    context = {
        'product': product,
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/admin_edit_product.html', context)

def buy_product(request, product_id):
    # Implement the logic for buying a product
    return HttpResponse(f"Product {product_id} bought successfully!")

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required(login_url='/login/')
def remove_from_cart(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('cart')

@login_required(login_url='/login/')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'web_app/cart.html', context)

@login_required(login_url='/login/')
def increase_quantity(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required(login_url='/login/')
def decrease_quantity(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    elif cart_item:
        cart_item.delete()
    return redirect('cart')

def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/product_details.html', context)

def payment_options(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
        'current_year': datetime.now().year
    }
    return render(request, 'web_app/payment_options.html', context)

@api_view(['POST'])
def process_payment(request):
    data = request.data.copy()
    user_id = data.get('user_id')
    if not user_id:
        return JsonResponse({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        data['user_id'] = int(user_id)
    except ValueError:
        return JsonResponse({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = PaymentSerializer(data=data)
    if serializer.is_valid():
        # Redirect to PayPal API
        paypal_url = "https://www.paypal.com/cgi-bin/webscr"
        params = {
            "cmd": "_xclick",
            "business": "your-paypal-dipakfulmlai70@gmail.com",
            "item_name": "Product Purchase",
            "amount": data['amount'],
            "currency_code": "USD",
            "notify_url": "https://paypal.me/DipakFulmali/paypal-ipn/",
            "return": "https://paypal.me/DipakFulmali/payment-success/",
            "cancel_return": "https://paypal.me/DipakFulmali/payment-cancel/",
        }
        response = requests.post(paypal_url, data=params)
        return redirect(response.url)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def add_card(request):
    if request.method == 'POST':
        card_number = request.POST['card_number']
        expiry_date = request.POST['expiry_date']
        cvv = request.POST['cvv']
        # Implement logic to save card details
        return redirect('home')
    return render(request, 'web_app/card.html')

@login_required(login_url='/login/')
def profile(request):
    return render(request, 'web_app/profile.html')

@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'web_app/change_password.html', {'form': form})

@login_required(login_url='/login/')
def upload_profile_photo(request):
    if request.method == 'POST':
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            request.user.profile.photo = profile_photo
            request.user.profile.save()
        return redirect('profile')
    return redirect('profile')
