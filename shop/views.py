from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from .models import Product, Category, Cart, Review, Order, OrderItem
from .forms import AddToCartForm, ReviewForm, EditProfileForm, ProductForm
from django.views.decorators.cache import cache_page
from django.core.cache import cache





@login_required
@transaction.atomic
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart')

    order = Order.objects.create(user=request.user, total=0)
    total = 0
    for item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.unit_price
        )
        total += item.product.unit_price * item.quantity
        item.delete()

    order.total = total
    order.save()

    return redirect('cart')


@login_required
def profile(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/profile.html', {'user_orders': user_orders})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'shop/edit_profile.html', {'form': form})


def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        products = Product.objects.filter(name__icontains=term)
        suggestions = list(products.values_list('name', flat=True))
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)


def product_search(request):
    query = request.GET.get('q')
    cache_key = f'product_search_{query}'
    products = cache.get(cache_key)

    if not products:
        products = Product.objects.filter(name__icontains=query)
        cache.set(cache_key, products, 60 * 15)  # Кэшировать на 15 минут

    return render(request, 'shop/product_search.html', {'products': products, 'query': query})


@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=product, defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def is_admin(user):
    return user.is_staff


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        if 'add_to_cart' in request.POST:
            form = AddToCartForm(request.POST, product=product)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                cart_item, created = Cart.objects.get_or_create(
                    user=request.user, product=product, defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                return redirect('cart')
        elif 'add_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('product_detail', id=product.id)
        elif 'edit_product' in request.POST and request.user.is_staff:
            edit_form = ProductForm(request.POST, request.FILES, instance=product)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('product_detail', id=product.id)
    else:
        form = AddToCartForm(product=product)
        review_form = ReviewForm()
        edit_form = ProductForm(instance=product) if request.user.is_staff else None

    reviews = Review.objects.filter(product=product)

    # Save product ID in cookie
    viewed_products = request.COOKIES.get('viewed_products', '')
    if str(product.id) not in viewed_products.split(','):
        viewed_products = f"{viewed_products},{product.id}" if viewed_products else str(product.id)

    response = render(request, 'shop/product_detail.html', {
        'product': product,
        'form': form,
        'reviews': reviews,
        'review_form': review_form,
        'categories': categories,
        'edit_form': edit_form
    })
    response.set_cookie('viewed_products', viewed_products, max_age=60 * 60 * 24 * 7)  # Cookie lasts for 1 week

    return response


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return JsonResponse({
                'success': True,
                'user': review.user.username,
                'rating': review.rating,
                'comment': review.comment
            })
    return JsonResponse({'success': False})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@cache_page(60 * 15)  # Кэшировать на 15 минут
def index(request):
    categories = Category.objects.all()
    latest_products = []

    for category in categories:
        latest_product = Product.objects.filter(category=category).order_by('-id').first()
        if latest_product:
            latest_products.append(latest_product)

    return render(request, 'shop/index.html', {
        'categories': categories,
        'latest_products': latest_products,
    })

@cache_page(60 * 15)  # Кэшировать на 15 минут
def category_products(request, id):
    category = get_object_or_404(Category, id=id)
    sort_by = request.GET.get('sort_by', 'default')
    if sort_by == 'price_asc':
        products = Product.objects.filter(category=category).order_by('unit_price')
    elif sort_by == 'price_desc':
        products = Product.objects.filter(category=category).order_by('-unit_price')
    else:
        products = Product.objects.filter(category=category)

    # Get viewed products from cookie
    viewed_products = request.COOKIES.get('viewed_products', '')
    viewed_product_ids = [int(pid) for pid in viewed_products.split(',') if pid.isdigit()]

    # Sort products: viewed products first
    viewed_products_list = products.filter(id__in=viewed_product_ids)
    other_products_list = products.exclude(id__in=viewed_product_ids)

    sorted_products = list(viewed_products_list) + list(other_products_list)

    categories = Category.objects.all()
    product_count = len(sorted_products)

    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': sorted_products,
        'categories': categories,
        'product_count': product_count,
        'sort_by': sort_by,
        'viewed_product_ids': viewed_product_ids,
    })


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    categories = Category.objects.all()
    total_sum = sum(item.quantity * item.product.unit_price for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'categories': categories,
        'total_sum': total_sum,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    categories = Category.objects.all()
    return render(request, 'shop/register.html', {'form': form, 'categories': categories})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    categories = Category.objects.all()
    return render(request, 'shop/login.html', {'categories': categories})


def user_logout(request):
    logout(request)
    return redirect('index')

def FitLife(request):
    return render(request, 'shop/FitLife.html')


