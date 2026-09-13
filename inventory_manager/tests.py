from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product, Customer, Order, OrderItem, Review
from .cart import Cart, COUPONS


class BunaiShoppingStorefrontTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Handloom Sarees",
            description="Pure silk and cotton weaves"
        )
        self.product = Product.objects.create(
            sku="BUN-HL-001",
            name="Chanderi Silk Saree",
            category=self.category,
            cost_price=Decimal("2000.00"),
            selling_price=Decimal("4000.00"),
            original_mrp=Decimal("5000.00"),
            stock_quantity=10,
            unit="piece",
            is_active=True,
            is_bestseller=True
        )

    def test_product_discount_and_stock(self):
        """Test discount percentage and stock status calculations."""
        # MRP: 5000, Selling: 4000 -> 20% discount
        self.assertEqual(self.product.discount_percent, 20)
        self.assertEqual(self.product.stock_status, "In Stock")

        # Test low stock
        self.product.stock_quantity = 3
        self.product.save()
        self.assertEqual(self.product.stock_status, "Only 3 left!")

    def test_storefront_pages_render(self):
        """Test home, shop catalog, product detail, and our story pages."""
        # Home
        res_home = self.client.get(reverse('home'))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "Bunai")

        # Shop
        res_shop = self.client.get(reverse('shop'))
        self.assertEqual(res_shop.status_code, 200)
        self.assertContains(res_shop, self.product.name)

        # Product Detail
        res_detail = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "₹4,000")

        # Our Story
        res_story = self.client.get(reverse('our_story'))
        self.assertEqual(res_story.status_code, 200)
        self.assertContains(res_story, "The Soul of Bunai")

    def test_shopping_cart_operations(self):
        """Test adding items to cart, updating quantity, and applying discount coupon."""
        # Add to cart
        add_res = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(add_res.status_code, 302)

        # Apply coupon BUNAI10 (10% off)
        coupon_res = self.client.post(reverse('cart_view'), {
            'apply_coupon': '1',
            'coupon_code': 'BUNAI10'
        })
        self.assertEqual(coupon_res.status_code, 302)

        # View cart with coupon applied
        cart_res = self.client.get(reverse('cart_view'))
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, self.product.name)
        self.assertContains(cart_res, "BUNAI10")

        # Verify cart totals
        cart = Cart(cart_res.wsgi_request)
        # Subtotal: 2 * 4000 = 8000
        self.assertEqual(cart.get_subtotal(), Decimal("8000.00"))
        # Discount: 10% of 8000 = 800
        self.assertEqual(cart.get_discount(), Decimal("800.00"))
        # Shipping fee: subtotal >= 1999 -> 0.00
        self.assertEqual(cart.get_shipping_fee(), Decimal("0.00"))
        # Grand total: 8000 - 800 = 7200
        self.assertEqual(cart.get_total(), Decimal("7200.00"))

    def test_checkout_and_order_placement_flow(self):
        """Test full checkout flow: adds to cart, submits checkout form, decrements stock, redirects to confirmation."""
        initial_stock = self.product.stock_quantity  # 10
        
        # Add item to cart
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2})

        checkout_data = {
            'full_name': 'Meera Desai',
            'email': 'meera@example.com',
            'phone': '9876543210',
            'shipping_address': 'Flat 101, Artisan Enclave',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'postal_code': '400001',
            'payment_method': 'UPI',
            'coupon_code': 'BUNAI10',
            'notes': 'Please call before delivery'
        }

        checkout_res = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(checkout_res.status_code, 302)

        # Verify order created in DB
        order = Order.objects.filter(customer__email='meera@example.com').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertEqual(order.discount_amount, Decimal("800.00"))
        self.assertEqual(order.grand_total, Decimal("7200.00"))

        # Verify stock was decremented: 10 - 2 = 8
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock - 2)

        # Verify Order Success Confirmation page
        success_res = self.client.get(reverse('order_success', args=[order.order_number]))
        self.assertEqual(success_res.status_code, 200)
        self.assertContains(success_res, order.order_number)

    def test_order_tracking_view(self):
        """Test looking up an order by order number and phone."""
        customer = Customer.objects.create(name="Rohan", email="rohan@example.com", phone="9988776655")
        order = Order.objects.create(customer=customer, status="PROCESSING")
        OrderItem.objects.create(order=order, product=self.product, quantity=1, unit_price=self.product.selling_price)

        track_res = self.client.post(reverse('track_order'), {
            'order_number': order.order_number,
            'contact_info': '9988776655'
        })
        self.assertEqual(track_res.status_code, 200)
        self.assertContains(track_res, order.order_number)
        self.assertContains(track_res, "In Crafting")

    def test_product_review_submission(self):
        """Test submitting a customer review."""
        review_res = self.client.post(reverse('add_review', args=[self.product.slug]), {
            'author_name': 'Aarav Patel',
            'rating': '5',
            'comment': 'Stunning texture and beautiful artisanal weave!'
        })
        self.assertEqual(review_res.status_code, 302)
        self.assertTrue(Review.objects.filter(author_name='Aarav Patel', product=self.product).exists())
