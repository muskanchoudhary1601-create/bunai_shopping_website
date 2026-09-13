from decimal import Decimal
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, OrderTrackingForm, ReviewForm
from .models import Category, Customer, Order, OrderItem, Product, Review


# ----------------------------------------------------------------------
# STOREFRONT HOME & CATALOG VIEWS
# ----------------------------------------------------------------------

def home(request):
    """Artisanal e-commerce storefront landing page."""
    categories = Category.objects.annotate(active_count=Count('products')).filter(active_count__gt=0)
    bestseller_products = Product.objects.filter(is_active=True, is_bestseller=True)[:4]
    if not bestseller_products.exists():
        bestseller_products = Product.objects.filter(is_active=True)[:4]
        
    featured_products = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:8]
    latest_reviews = Review.objects.select_related('product')[:6]

    context = {
        'categories': categories,
        'bestseller_products': bestseller_products,
        'featured_products': featured_products,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'store/home.html', context)


def shop(request):
    """Full product catalog with search, category filtering, price filtering, and sorting."""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    
    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(craft_technique__icontains=q) |
            Q(material_origin__icontains=q)
        )
        
    # Category filter
    selected_category_slug = request.GET.get('category')
    current_category = None
    if selected_category_slug:
        current_category = Category.objects.filter(slug=selected_category_slug).first()
        if current_category:
            queryset = queryset.filter(category=current_category)
            
    # Price Range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            queryset = queryset.filter(selling_price__gte=Decimal(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            queryset = queryset.filter(selling_price__lte=Decimal(max_price))
        except ValueError:
            pass
            
    # Availability filter
    in_stock_only = request.GET.get('in_stock') == '1'
    if in_stock_only:
        queryset = queryset.filter(stock_quantity__gt=0)
        
    # Sorting
    sort = request.GET.get('sort', 'featured')
    sort_mapping = {
        'featured': ['-is_bestseller', '-is_featured', '-created_at'],
        'price_low': ['selling_price'],
        'price_high': ['-selling_price'],
        'rating': ['-rating', '-review_count'],
        'newest': ['-created_at'],
    }
    order_fields = sort_mapping.get(sort, ['-is_bestseller', '-created_at'])
    queryset = queryset.order_by(*order_fields)
    
    # Pagination
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.annotate(total_active=Count('products')).all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': current_category,
        'selected_category_slug': selected_category_slug,
        'q': q,
        'selected_sort': sort,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock_only': in_stock_only,
        'total_count': queryset.count(),
    }
    return render(request, 'store/shop.html', context)


def product_detail(request, slug):
    """Artisan product detail view with craft specs, reviews, and related items."""
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    reviews = product.reviews.all()
    review_form = ReviewForm()
    
    # Related products from same category or featured
    related_products = Product.objects.filter(is_active=True).exclude(pk=product.pk)
    if product.category:
        related_products = related_products.filter(category=product.category)
    related_products = related_products[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


@require_POST
def add_review(request, slug):
    """Submit a customer product review."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.save()
        
        # Update product average rating & review count
        all_reviews = product.reviews.all()
        avg_rating = sum(r.rating for r in all_reviews) / max(1, all_reviews.count())
        product.rating = round(Decimal(avg_rating), 1)
        product.review_count = all_reviews.count()
        product.save()
        
        messages.success(request, "Thank you! Your artisan craft review has been posted.")
    else:
        messages.error(request, "Please fill out all review fields properly.")
    return redirect('product_detail', slug=product.slug)


# ----------------------------------------------------------------------
# SHOPPING CART VIEWS
# ----------------------------------------------------------------------

def cart_view(request):
    """Shopping cart page with coupon discount and total breakdown."""
    cart = Cart(request)
    
    # Handle coupon code submission via GET or POST
    if request.method == 'POST' and 'apply_coupon' in request.POST:
        code = request.POST.get('coupon_code', '')
        success, msg = cart.apply_coupon(code)
        if success:
            messages.success(request, f"Coupon applied: {msg}")
        else:
            messages.error(request, msg)
        return redirect('cart_view')

    if request.method == 'POST' and 'remove_coupon' in request.POST:
        cart.remove_coupon()
        messages.info(request, "Coupon removed.")
        return redirect('cart_view')

    context = {
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add(request, product_id):
    """Add product to shopping cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if product.is_out_of_stock:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect('product_detail', slug=product.slug)

    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.total_items,
            'cart_total': float(cart.get_total()),
            'message': f"Added {quantity}x '{product.name}' to your cart!",
        })
        
    messages.success(request, f"Added '{product.name}' to your shopping cart!")
    if request.POST.get('buy_now') == '1':
        return redirect('checkout')
    return redirect(request.META.get('HTTP_REFERER') or 'cart_view')


@require_POST
def cart_update(request, product_id):
    """Update item quantity in shopping cart."""
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product_id=product_id, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.total_items,
            'subtotal': float(cart.get_subtotal()),
            'discount': float(cart.get_discount()),
            'shipping': float(cart.get_shipping_fee()),
            'total': float(cart.get_total()),
        })
        
    return redirect('cart_view')


@require_POST
def cart_remove(request, product_id):
    """Remove item from shopping cart."""
    cart = Cart(request)
    cart.remove(product_id=product_id)
    messages.info(request, "Item removed from cart.")
    return redirect('cart_view')


# ----------------------------------------------------------------------
# CHECKOUT & ORDER PLACEMENT
# ----------------------------------------------------------------------

def checkout(request):
    """Customer checkout and payment placement."""
    cart = Cart(request)
    if cart.is_empty:
        messages.warning(request, "Your shopping cart is empty. Please add items to proceed.")
        return redirect('shop')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                full_name = form.cleaned_data['full_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data['shipping_address']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                postal_code = form.cleaned_data['postal_code']
                payment_method = form.cleaned_data['payment_method']
                notes = form.cleaned_data['notes']
                coupon_code = form.cleaned_data['coupon_code'] or cart.coupon_code or ''

                if coupon_code:
                    cart.apply_coupon(coupon_code)

                # Find or create customer
                customer = Customer.objects.filter(email=email).first()
                if not customer:
                    customer = Customer.objects.create(
                        name=full_name,
                        email=email,
                        phone=phone,
                        address=address,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                    )
                else:
                    customer.name = full_name
                    customer.phone = phone
                    customer.address = address
                    customer.city = city
                    customer.state = state
                    customer.postal_code = postal_code
                    customer.save()

                # Determine initial payment status
                payment_status = 'PAID' if payment_method in ['UPI', 'CARD', 'NET_BANKING'] else 'COD_PENDING'

                # Create Order
                order = Order.objects.create(
                    customer=customer,
                    status='PENDING',
                    payment_status=payment_status,
                    payment_method=payment_method,
                    shipping_address=f"{address}, {city}, {state} - {postal_code}",
                    coupon_code=coupon_code,
                    discount_amount=cart.get_discount(),
                    tax_rate_percent=Decimal('0.00'),
                    shipping_fee=cart.get_shipping_fee(),
                    notes=notes,
                )

                # Create OrderItems and decrement stock
                for item in cart:
                    product = item['product']
                    quantity = item['quantity']
                    price = item['price']

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=price,
                    )

                    # Decrement inventory stock
                    product.stock_quantity = max(0, product.stock_quantity - quantity)
                    product.save()

                # Clear shopping cart
                cart.clear()

                messages.success(request, f"Thank you! Your order #{order.order_number} has been placed successfully.")
                return redirect('order_success', order_number=order.order_number)
        else:
            messages.error(request, "Please check the form and fill in all required shipping details.")
    else:
        initial_data = {}
        if cart.coupon_code:
            initial_data['coupon_code'] = cart.coupon_code
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_number):
    """Order confirmation and receipt page."""
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related('items__product'),
        order_number=order_number
    )
    return render(request, 'store/order_success.html', {'order': order})


def track_order(request):
    """Customer order tracking lookup and timeline."""
    order = None
    searched = False
    order_num = request.POST.get('order_number') or request.GET.get('order_number') or ''
    contact = request.POST.get('contact_info') or request.GET.get('contact') or ''
    
    if order_num:
        order_num = order_num.strip().upper()
        searched = True
        queryset = Order.objects.filter(order_number=order_num).select_related('customer').prefetch_related('items__product')
        if contact:
            contact = contact.strip()
            queryset = queryset.filter(
                Q(customer__phone__icontains=contact) |
                Q(customer__email__icontains=contact) |
                Q(customer__name__icontains=contact)
            )
        order = queryset.first()
        if not order:
            messages.error(request, f"No order found matching #{order_num}. Please check your order details.")

    form = OrderTrackingForm()
    return render(request, 'store/track_order.html', {
        'form': form,
        'order': order,
        'searched': searched,
        'order_number_query': order_num,
        'contact_info_query': contact,
    })


def our_story(request):
    """Artisan heritage, values, and craft story page."""
    return render(request, 'store/our_story.html')
