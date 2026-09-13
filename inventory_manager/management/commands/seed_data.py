from decimal import Decimal
from datetime import timedelta
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory_manager.models import Category, Product, Customer, Order, OrderItem, Review


class Command(BaseCommand):
    help = 'Seeds database with realistic artisan shopping catalog, reviews, customers, and order tracking data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Clearing old data..."))
        Review.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Creating Curated Craft Categories..."))
        categories_data = [
            {
                "name": "Handloom Sarees & Textiles",
                "description": "Authentic handloom Chanderi, Banarasi, and organic cotton weaves direct from master weaver clusters.",
                "icon": "bi-basket",
            },
            {
                "name": "Boho Macrame & Wall Decor",
                "description": "Hand-knotted 100% natural cotton cord wall tapestries, plant hangers, and rustic room accents.",
                "icon": "bi-flower1",
            },
            {
                "name": "Studio Pottery & Ceramics",
                "description": "Wheel-thrown, lead-free glazed tableware, tea sets, terracotta mugs, and artisanal clay pots.",
                "icon": "bi-cup-hot",
            },
            {
                "name": "Woodcraft & Bamboo Art",
                "description": "Reclaimed natural sheesham wood tableware, brass inlaid organizers, and eco-friendly bamboo crafts.",
                "icon": "bi-tree",
            },
            {
                "name": "Kashmiri & Kantha Needlecraft",
                "description": "Intricate needlework, pure wool shawls, chain-stitched linen cushion covers, and vintage clutch bags.",
                "icon": "bi-scissors",
            },
            {
                "name": "Crochet & Hand-Knit Woolens",
                "description": "Cozy merino wool throws, handcrafted granny-square tote bags, and warm artisanal knitwear.",
                "icon": "bi-handbag",
            },
        ]

        categories = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cdata["name"],
                defaults={
                    "description": cdata["description"],
                    "icon": cdata["icon"],
                }
            )
            categories[cat.name] = cat

        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} categories."))

        self.stdout.write(self.style.SUCCESS("Creating Artisanal Products..."))
        products_data = [
            {
                "sku": "BUN-HL-001",
                "name": "Handwoven Pure Chanderi Silk Saree with Gold Zari",
                "category": categories["Handloom Sarees & Textiles"],
                "description": "Exquisite handloom Chanderi silk saree featuring delicate golden zari booties, woven on traditional pit looms by heritage artisan families in Madhya Pradesh. Lightweight, airy, and shimmering with subtle royal sheen.",
                "material_origin": "Chanderi, Madhya Pradesh",
                "craft_technique": "Traditional Pit-Loom Weaving & Zari Work",
                "original_mrp": Decimal("5999.00"),
                "selling_price": Decimal("4499.00"),
                "stock_quantity": 8,
                "unit": "piece",
                "rating": Decimal("4.9"),
                "review_count": 28,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "sku": "BUN-MAC-002",
                "name": "Boho Geometric Macrame Large Wall Hanging",
                "category": categories["Boho Macrame & Wall Decor"],
                "description": "Hand-knotted from 100% natural unbleached cotton rope on seasoned sustainable driftwood. Designed with intricate geometric chevron diamonds and soft flowing fringes to add cozy boho charm to any room.",
                "material_origin": "Jaipur, Rajasthan",
                "craft_technique": "Hand-Knotted Fiber Art",
                "original_mrp": Decimal("2499.00"),
                "selling_price": Decimal("1799.00"),
                "stock_quantity": 12,
                "unit": "piece",
                "rating": Decimal("4.8"),
                "review_count": 19,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "sku": "BUN-EMB-003",
                "name": "Kashmiri Aari Embroidered Linen Cushion Covers (Set of 2)",
                "category": categories["Kashmiri & Kantha Needlecraft"],
                "description": "Pair of pure natural linen cushion covers adorned with delicate floral Kashmiri Aari chain-stitch embroidery in warm earthy hues. Features invisible zipper closures.",
                "material_origin": "Srinagar, Kashmir",
                "craft_technique": "Hand Aari Hook Embroidery",
                "original_mrp": Decimal("1899.00"),
                "selling_price": Decimal("1299.00"),
                "stock_quantity": 15,
                "unit": "set",
                "rating": Decimal("4.9"),
                "review_count": 34,
                "is_featured": True,
                "is_bestseller": False,
            },
            {
                "sku": "BUN-POT-004",
                "name": "Terracotta Hand-Painted Warli Coffee Mugs (Set of 4)",
                "category": categories["Studio Pottery & Ceramics"],
                "description": "Food-safe glazed natural terracotta mugs hand-painted with tribal Warli celebration motifs. Keeps coffee and chai hot while offering rustic tactile joy with every sip.",
                "material_origin": "Khurja & Bastar Guilds",
                "craft_technique": "Wheel Pottery & Tribal Warli Art",
                "original_mrp": Decimal("1299.00"),
                "selling_price": Decimal("949.00"),
                "stock_quantity": 4,  # Low stock
                "unit": "set",
                "rating": Decimal("4.7"),
                "review_count": 16,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "sku": "BUN-WD-005",
                "name": "Handcrafted Sheesham Wood Cutlery Holder with Brass Inlay",
                "category": categories["Woodcraft & Bamboo Art"],
                "description": "Hand-carved Indian rosewood organizer featuring 3 partitions and traditional star-shaped brass inlay. Finished with organic food-grade beeswax polish.",
                "material_origin": "Saharanpur, Uttar Pradesh",
                "craft_technique": "Wood Joinery & Tarkashi Brass Inlay",
                "original_mrp": Decimal("1199.00"),
                "selling_price": Decimal("849.00"),
                "stock_quantity": 20,
                "unit": "piece",
                "rating": Decimal("4.8"),
                "review_count": 22,
                "is_featured": False,
                "is_bestseller": False,
            },
            {
                "sku": "BUN-KNT-006",
                "name": "Hand-Knitted Chunky Merino Wool Throw Blanket",
                "category": categories["Crochet & Hand-Knit Woolens"],
                "description": "Heirloom-grade chunky knit throw blanket crafted from 100% fine Australian merino wool. Extremely soft, breathable, and provides warm textured comfort for bed or sofa.",
                "material_origin": "Himachal Pradesh",
                "craft_technique": "Hand Needle Knitwear",
                "original_mrp": Decimal("4999.00"),
                "selling_price": Decimal("3699.00"),
                "stock_quantity": 3,
                "unit": "piece",
                "rating": Decimal("5.0"),
                "review_count": 14,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "sku": "BUN-HL-007",
                "name": "Indigo Hand Block-Printed Cotton Mulmul AC Dohar",
                "category": categories["Handloom Sarees & Textiles"],
                "description": "Triple-layer authentic Jaipuri cotton mulmul summer blanket with reversible natural indigo Bagru block prints. Incredibly lightweight, breathable, and soft.",
                "material_origin": "Bagru & Sanganer, Jaipur",
                "craft_technique": "Natural Dye Hand Block Printing",
                "original_mrp": Decimal("2499.00"),
                "selling_price": Decimal("1899.00"),
                "stock_quantity": 14,
                "unit": "piece",
                "rating": Decimal("4.8"),
                "review_count": 41,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "sku": "BUN-POT-008",
                "name": "Speckled Stoneware Hand-Thrown Matcha & Soup Bowl",
                "category": categories["Studio Pottery & Ceramics"],
                "description": "Wheel-thrown rustic stoneware chawan bowl finished in a calming matte sage glaze with subtle earthy speckles. Microwave and dishwasher safe.",
                "material_origin": "Auroville Studio Guilds",
                "craft_technique": "High-Fired Studio Ceramics",
                "original_mrp": Decimal("1199.00"),
                "selling_price": Decimal("849.00"),
                "stock_quantity": 9,
                "unit": "piece",
                "rating": Decimal("4.9"),
                "review_count": 11,
                "is_featured": False,
                "is_bestseller": False,
            },
            {
                "sku": "BUN-KNT-009",
                "name": "Sunflower Granny-Square Handcrafted Crochet Tote Bag",
                "category": categories["Crochet & Hand-Knit Woolens"],
                "description": "Charming vibrant sunflower crochet tote made from sturdy combed cotton yarn with double reinforced handles and interior canvas lining.",
                "material_origin": "Bengaluru Craft Collective",
                "craft_technique": "Vintage Crochet Needlecraft",
                "original_mrp": Decimal("1599.00"),
                "selling_price": Decimal("1199.00"),
                "stock_quantity": 11,
                "unit": "piece",
                "rating": Decimal("4.9"),
                "review_count": 27,
                "is_featured": True,
                "is_bestseller": False,
            },
        ]

        products = []
        for pdata in products_data:
            prod = Product.objects.create(**pdata)
            products.append(prod)

        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} products."))

        self.stdout.write(self.style.SUCCESS("Creating Customer Reviews..."))
        reviews_data = [
            ("Ananya Sharma", 5, "The Chanderi saree is beyond gorgeous! The texture is so soft and the zari has the subtlest golden glow. Packaged with zero plastic which I love!", products[0]),
            ("Pooja Hegde", 5, "Pure craftsmanship. You can instantly tell this was handwoven by true artisans.", products[0]),
            ("Rohan Kapoor", 5, "The macrame wall hanging completely transformed our living room. Sturdy, beautiful, and arrived in 3 days.", products[1]),
            ("Sneha Patel", 5, "The Kashmiri cushion covers look straight out of an upscale boutique. The needlework is intricate and immaculate.", products[2]),
            ("Vikramaditya M.", 4, "Great terracotta mugs, perfect for morning espresso and chai. Authentic earthy aroma.", products[3]),
            ("Meera Desai", 5, "The dohar blanket is like sleeping on a cloud. Authentic indigo block print on pure cotton mulmul.", products[6]),
        ]

        for author, rating, comment, prod in reviews_data:
            Review.objects.create(
                product=prod,
                author_name=author,
                rating=rating,
                comment=comment,
                is_verified_buyer=True
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(reviews_data)} verified reviews."))

        self.stdout.write(self.style.SUCCESS("Creating Demo Customer & Orders for Tracking..."))
        customer = Customer.objects.create(
            name="Ananya Sharma",
            email="ananya@example.com",
            phone="9820145678",
            address="Flat 402, Sea Breeze Apts, Bandra West",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400050"
        )

        now = timezone.now()
        # Order 1: In Crafting / Processing (Great for testing track order!)
        order1 = Order.objects.create(
            customer=customer,
            order_date=now - timedelta(days=1),
            status="PROCESSING",
            payment_status="PAID",
            payment_method="UPI",
            coupon_code="BUNAI10",
            discount_amount=Decimal("450.00"),
            shipping_fee=Decimal("0.00"),
            shipping_address=customer.address,
            notes="Please wrap with eco-friendly craft paper.",
        )
        OrderItem.objects.create(order=order1, product=products[0], quantity=1, unit_price=products[0].selling_price)
        OrderItem.objects.create(order=order1, product=products[2], quantity=1, unit_price=products[2].selling_price)

        self.stdout.write(self.style.SUCCESS(f"Created demo trackable order #{order1.order_number} for customer {customer.name}!"))
        self.stdout.write(self.style.SUCCESS("Bunai shopping storefront database seeded successfully!"))
