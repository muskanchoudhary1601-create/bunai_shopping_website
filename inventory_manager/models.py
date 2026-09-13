from decimal import Decimal
import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-box-seam', help_text='Bootstrap icon class name (e.g. bi-palette, bi-scissors)')
    image_url = models.CharField(max_length=500, blank=True, help_text="Optional banner image URL")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, help_text="Unique Stock Keeping Unit, e.g. BUN-TEX-001")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    description = models.TextField(blank=True)
    material_origin = models.CharField(max_length=200, blank=True, default="100% Handcrafted in India", help_text="e.g. Chanderi, Madhya Pradesh")
    craft_technique = models.CharField(max_length=200, blank=True, default="Traditional Handloom & Artisan Craft")
    original_mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original MRP before discount")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Artisan production/acquisition cost")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Retail selling price")
    stock_quantity = models.IntegerField(default=10, help_text="Current available quantity")
    low_stock_threshold = models.IntegerField(default=5, help_text="Alert threshold for low inventory")
    unit = models.CharField(max_length=20, default='piece', help_text="Unit of measure (e.g. piece, set, meter, pair)")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('4.8'))
    review_count = models.PositiveIntegerField(default=12)
    is_featured = models.BooleanField(default=True, help_text="Display on homepage featured section")
    is_bestseller = models.BooleanField(default=False, help_text="Mark as bestseller badge")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_bestseller", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.original_mrp or self.original_mrp < self.selling_price:
            self.original_mrp = round(self.selling_price * Decimal('1.25'), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (₹{self.selling_price})"

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percent(self):
        if self.original_mrp and self.original_mrp > self.selling_price:
            return int(round(((self.original_mrp - self.selling_price) / self.original_mrp) * 100))
        return 0

    @property
    def stock_status(self):
        if self.is_out_of_stock:
            return "Out of Stock"
        if self.is_low_stock:
            return f"Only {self.stock_quantity} left!"
        return "In Stock"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.phone or self.email or 'Client'})"

    @property
    def location_display(self):
        parts = [self.city, self.state, self.postal_code]
        return ", ".join(p for p in parts if p) or "India"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Order Placed'),
        ('PROCESSING', 'In Crafting / Packing'),
        ('SHIPPED', 'Dispatched / In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Pending Payment'),
        ('PAID', 'Paid Online'),
        ('COD_PENDING', 'Cash on Delivery (Pending)'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI / QR Code / Instant Pay'),
        ('COD', 'Cash on Delivery (COD)'),
        ('CARD', 'Credit / Debit Card'),
        ('NET_BANKING', 'Net Banking'),
    ]

    order_number = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    shipping_address = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True)
    tax_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), blank=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), blank=True)
    notes = models.TextField(blank=True, help_text="Delivery instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date", "-id"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            prefix = "BN"
            today_str = timezone.now().strftime("%Y%m")
            random_suffix = uuid.uuid4().hex[:5].upper()
            self.order_number = f"{prefix}-{today_str}-{random_suffix}"
        if not self.shipping_address and self.customer:
            self.shipping_address = self.customer.address
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.name}"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def tax_amount(self):
        if self.tax_rate_percent > 0:
            taxable_base = max(Decimal('0.00'), self.subtotal - self.discount_amount)
            return round(taxable_base * (self.tax_rate_percent / Decimal('100.0')), 2)
        return Decimal('0.00')

    @property
    def grand_total(self):
        total = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_fee
        return max(Decimal('0.00'), round(total, 2))

    @property
    def total_items_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def progress_percentage(self):
        mapping = {
            'PENDING': 25,
            'PROCESSING': 55,
            'SHIPPED': 80,
            'DELIVERED': 100,
            'CANCELLED': 0,
        }
        return mapping.get(self.status, 25)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ ₹{self.unit_price}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    is_verified_buyer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name} - {self.rating}★ on {self.product.name}"
