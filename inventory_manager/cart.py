from decimal import Decimal
from .models import Product


COUPONS = {
    'BUNAI10': {'type': 'percent', 'value': Decimal('10.0'), 'label': '10% Welcome Artisan Discount'},
    'CRAFT200': {'type': 'fixed', 'value': Decimal('200.0'), 'label': '₹200 Off Craft Voucher (Min. ₹1,000)'},
    'FESTIVE15': {'type': 'percent', 'value': Decimal('15.0'), 'label': '15% Festive Handloom Offer'},
}


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        self.coupon_code = self.session.get('coupon_code')

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.selling_price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] += int(quantity)

        # Ensure we don't exceed available stock
        if self.cart[product_id]['quantity'] > product.stock_quantity and product.stock_quantity > 0:
            self.cart[product_id]['quantity'] = product.stock_quantity

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product.id)
        else:
            self.save()

    def update(self, product_id, quantity):
        prod_id = str(product_id)
        if prod_id in self.cart:
            qty = int(quantity)
            if qty > 0:
                try:
                    product = Product.objects.get(id=int(prod_id))
                    self.cart[prod_id]['quantity'] = min(qty, product.stock_quantity)
                except Product.DoesNotExist:
                    self.cart[prod_id]['quantity'] = qty
                self.save()
            else:
                self.remove(prod_id)

    def remove(self, product_id):
        prod_id = str(product_id)
        if prod_id in self.cart:
            del self.cart[prod_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.session['coupon_code'] = None
        self.save()

    def save(self):
        self.session.modified = True

    def apply_coupon(self, code):
        code = code.strip().upper()
        if code in COUPONS:
            self.session['coupon_code'] = code
            self.coupon_code = code
            self.save()
            return True, COUPONS[code]['label']
        return False, "Invalid promo or coupon code."

    def remove_coupon(self):
        self.session['coupon_code'] = None
        self.coupon_code = None
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = self.cart.copy()

        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def total_items(self):
        return len(self)

    @property
    def is_empty(self):
        return len(self) == 0

    def get_subtotal(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_discount(self):
        subtotal = self.get_subtotal()
        if not self.coupon_code or self.coupon_code not in COUPONS or subtotal <= 0:
            return Decimal('0.00')

        coupon = COUPONS[self.coupon_code]
        if coupon['type'] == 'percent':
            return round(subtotal * (coupon['value'] / Decimal('100.0')), 2)
        elif coupon['type'] == 'fixed':
            if subtotal >= Decimal('1000.00'):
                return min(subtotal, coupon['value'])
        return Decimal('0.00')

    def get_shipping_fee(self):
        subtotal = self.get_subtotal()
        if subtotal == 0 or subtotal >= Decimal('1999.00'):
            return Decimal('0.00')
        return Decimal('99.00')

    def get_free_shipping_threshold_remaining(self):
        subtotal = self.get_subtotal()
        if subtotal >= Decimal('1999.00'):
            return Decimal('0.00')
        return Decimal('1999.00') - subtotal

    def get_free_shipping_progress(self):
        subtotal = self.get_subtotal()
        if subtotal >= Decimal('1999.00'):
            return 100
        return int(round((subtotal / Decimal('1999.00')) * 100))

    def get_total(self):
        subtotal = self.get_subtotal()
        discount = self.get_discount()
        shipping = self.get_shipping_fee()
        return max(Decimal('0.00'), subtotal - discount + shipping)
