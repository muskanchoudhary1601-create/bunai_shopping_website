from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Customer, Order, OrderItem

# Customize Django Admin Branding
admin.site.site_header = "Bunai Artisan Inventory & Order Hub"
admin.site.site_title = "Bunai Admin Portal"
admin.site.index_title = "Handmade Goods Management & Operations"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'product_count_display', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def product_count_display(self, obj):
        return obj.products.count()
    product_count_display.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'stock_badge', 'unit', 'profit_margin_display', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    list_editable = ['selling_price', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    def stock_badge(self, obj):
        color = 'green' if not obj.is_low_stock and not obj.is_out_of_stock else ('orange' if obj.is_low_stock else 'red')
        return format_html(
            '<span style="font-weight: bold; color: {};">{} ({})</span>',
            color,
            obj.stock_quantity,
            obj.stock_status
        )
    stock_badge.short_description = "Stock"

    def profit_margin_display(self, obj):
        return f"{obj.profit_margin}%"
    profit_margin_display.short_description = "Margin"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'state', 'orders_count_display', 'created_at']
    search_fields = ['name', 'email', 'phone', 'city', 'notes']
    list_filter = ['state', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    def orders_count_display(self, obj):
        return obj.orders.count()
    orders_count_display.short_description = "Total Orders"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'subtotal_display']
    readonly_fields = ['subtotal_display']

    def subtotal_display(self, obj):
        if obj.pk:
            return f"₹{obj.total_price:,.2f}"
        return "-"
    subtotal_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'status_badge', 'payment_badge', 'payment_method', 'items_count', 'grand_total_display']
    list_filter = ['status', 'payment_status', 'payment_method', 'order_date']
    search_fields = ['order_number', 'customer__name', 'customer__phone', 'customer__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'grand_total']
    inlines = [OrderItemInline]
    actions = ['mark_as_delivered', 'mark_as_paid', 'mark_as_processing']

    fieldsets = (
        ("Order Information", {
            'fields': ('order_number', 'customer', 'order_date', 'status', 'shipping_address', 'notes')
        }),
        ("Payment & Financials", {
            'fields': ('payment_status', 'payment_method', 'discount_amount', 'tax_rate_percent', 'shipping_fee')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'PENDING': '#d97706',
            'PROCESSING': '#2563eb',
            'SHIPPED': '#0284c7',
            'DELIVERED': '#16a34a',
            'CANCELLED': '#dc2626',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 500;">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def payment_badge(self, obj):
        colors = {
            'PAID': '#16a34a',
            'UNPAID': '#dc2626',
            'PARTIAL': '#d97706',
            'REFUNDED': '#64748b',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 500;">{}</span>',
            colors.get(obj.payment_status, '#64748b'),
            obj.get_payment_status_display()
        )
    payment_badge.short_description = "Payment"

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items"

    def grand_total_display(self, obj):
        return f"₹{obj.grand_total:,.2f}"
    grand_total_display.short_description = "Grand Total"

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
        self.message_user(request, "Selected orders marked as Delivered.")

    @admin.action(description="Mark selected orders as Paid")
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='PAID')
        self.message_user(request, "Selected orders marked as Paid.")

    @admin.action(description="Mark selected orders as Processing")
    def mark_as_processing(self, request, queryset):
        queryset.update(status='PROCESSING')
        self.message_user(request, "Selected orders marked as Processing.")
