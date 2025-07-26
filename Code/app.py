import os
import json
import datetime
import io
import base64
import qrcode
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'Monkey'  # Replace with a strong secret in production

ORDERS_FILE = 'orders.json'
REVIEWS_FILE = 'reviews.json'
FSSAI_LICENSE = "21022071000137"

AVAILABILITY = {}

# ------------------------------------------------------------------
# Full Menu Data (organized by category)
# ------------------------------------------------------------------
DEFAULT_MENU = {
    "Tandoori": [
        {
            "name": "Tandoori chicken",
            "options": [
                {"size": "half", "price": 300, "description": "Half portion (4 pieces)"},
                {"size": "full", "price": 550, "description": "Full portion (8 pieces)"}
            ]
        },
        {
            "name": "Afghani chicken",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion (4 pieces)"},
                {"size": "full", "price": 650, "description": "Full portion (8 pieces)"}
            ]
        },
        {
            "name": "Chicken tika",
            "options": [
                {"size": "half", "price": 250, "description": "Half portion (6 pieces)"},
                {"size": "full", "price": 500, "description": "Full portion (12 pieces)"}
            ]
        },
        {
            "name": "Malai tika",
            "options": [
                {"size": "half", "price": 300, "description": "Half portion (6 pieces)"},
                {"size": "full", "price": 550, "description": "Full portion (12 pieces)"}
            ]
        },
        {
            "name": "Fish tika",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion (8 pieces)"},
                {"size": "full", "price": 400, "description": "Full portion (16 pieces)"}
            ]
        }
    ],
    "Barbeque": [
        {"name": "Mutton barbeque", "price": 150, "description": "Non-veg item. Chicken barbeque. Costs: 150 rupees."},
        {"name": "Chicken barbeque", "price": 120, "description": "Non-veg item. Chicken barbeque. Costs: 120 rupees."},
        {"name": "Fish barbeque", "price": 120, "description": "Non-veg item. Fish barbeque. Costs: 120 rupees."}
    ],
    "Momos": [
        {"name": "Steamed momos", "price": 120, "description": "Non-veg item. Steamed momos. Bestseller. Costs: 120 rupees."},
        {"name": "Fry momos", "price": 140, "description": "Non-veg item. Fry momos. Costs: 140 rupees."},
        {"name": "Tandoori momos", "price": 170, "description": "Non-veg item. Tandoori momos. Costs: 170 rupees."},
        {"name": "Kurkure momos", "price": 250, "description": "Non-veg item. Kurkure momos. Costs: 250 rupees."},
        {"name": "Malai momos", "price": 250, "description": "Non-veg item. Malai momos. Costs: 250 rupees."},
        {"name": "Afghani momos", "price": 250, "description": "Non-veg item. Afghani momos. Costs: 250 rupees."}
    ],
    "Rolls": [
        {"name": "Chicken shawarma", "price": 180, "description": "Non-veg item. Chicken shawarma. Bestseller. Costs: 180 rupees."},
        {"name": "Tika roll", "price": 180, "description": "Veg Item. Tika roll. Costs: 180 rupees."},
        {"name": "Afghani roll", "price": 180, "description": "Veg Item. Afghani roll. Costs: 180 rupees."},
        {"name": "Malai roll", "price": 180, "description": "Veg Item. Malai roll. Costs: 180 rupees."}
    ],
    "Non Veg": [
        {
            "name": "Butter chicken",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion"},
                {"size": "full", "price": 650, "description": "Full portion"}
            ]
        },
        {
            "name": "Chicken changezi",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion"},
                {"size": "full", "price": 650, "description": "Full portion"}
            ]
        },
        {
            "name": "Mughlai chicken",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion"},
                {"size": "full", "price": 650, "description": "Full portion"}
            ]
        },
        {
            "name": "Malaie chicken",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion"},
                {"size": "full", "price": 650, "description": "Full portion"}
            ]
        },
        {
            "name": "Chicken curry",
            "options": [
                {"size": "half", "price": 300, "description": "Half portion"},
                {"size": "full", "price": 550, "description": "Full portion"}
            ]
        }
    ],
    "Fried": [
    {
        "name": "Fry chicken",
        "options": [
            {"size": "half", "price": 300, "description": "Half portion (4 pieces)"},
            {"size": "full", "price": 500, "description": "Full portion (8 pieces)"}
        ]
    },
    {
        "name": "Chicken kanti",
        "options": [
            {"size": "half", "price": 200, "description": "Half portion (6 pieces)"},
            {"size": "full", "price": 300, "description": "Full portion (12 pieces)"}
        ]
    },
    {
        "name": "Mutton kanti",
        "options": [
            {"size": "half", "price": 300, "description": "Half portion (6 pieces)"},
            {"size": "full", "price": 500, "description": "Full portion (12 pieces)"}
        ]
    },
    {
        "name": "Fish fry",
        "options": [
            {"size": "half", "price": 150, "description": "Half portion (8 pieces)"},
            {"size": "full", "price": 250, "description": "Full portion (16 pieces)"}
        ]
    },
    {
        "name": "Mutton kabab",
        "price": 240,
        "description": "Mutton kabab"
    },
    {
        "name": "Chicken kabab",
        "price": 100,
        "description": "Chicken kabab"
    }
    ],

     "Chinese": [
        {
            "name": "Chilli chicken",
            "options": [
                {"size": "half", "price": 250, "description": "Half portion"},
                {"size": "full", "price": 500, "description": "Full portion"}
            ]
        },
        {
            "name": "Chicken munchurian",
            "options": [
                {"size": "half", "price": 350, "description": "Half portion"},
                {"size": "full", "price": 650, "description": "Full portion"}
            ]
        },
        {
            "name": "Chicken fried rice",
            "price": 250,
            "description": "Full portion"
        },
        {
            "name": "Veg fried rice",
            "price": 200,
            "description": "Full portion"
        },
{
            "name": "Chicken Chowmin",
            "price": 180,
            "description": "Full portion"
        },
{
            "name": "Veg Chowmin",
            "price": 150,
            "description": "Full portion"
        }
    ],
    "Veg": [
        {
            "name": "Tomato paneer",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Shahi paneer",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Rajma masala",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Dal makhani",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Matar malai mushroom",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Chana Masala",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Dal Fry",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        },
        {
            "name": "Mix Veg",
            "options": [
                {"size": "half", "price": 200, "description": "Half portion"},
                {"size": "full", "price": 300, "description": "Full portion"}
            ]
        }
    ],
    "Rice": [
    {
        "name": "Chicken biryani",
        "options": [
            {"size": "half", "price": 100, "description": "Half portion"},
            {"size": "full", "price": 160, "description": "Full portion"}
        ]
    },
    {
        "name": "Plain rice",
        "options": [
            {"size": "half", "price": 50, "description": "Half portion"},
            {"size": "full", "price": 100, "description": "Full portion"}
        ]
    },
    {
        "name": "Zeera rice",
        "options": [
            {"size": "half", "price": 80, "description": "Half portion"},
            {"size": "full", "price": 150, "description": "Full portion"}
        ]
    }
],
    "Breads": [
        {"name": "Tawa rooti", "price": 20, "description": "Veg Item. Tawa rooti. Costs: 20 rupees."},
        {"name": "Butter naan", "price": 70, "description": "Veg Item. Butter naan. Costs: 70 rupees."},
        {"name": "Plain naan", "price": 50, "description": "Veg Item. Plain naan. Bestseller. Costs: 50 rupees."},
        {"name": "Garlic naan", "price": 70, "description": "Veg Item. Garlic naan. Costs: 70 rupees."},
        {"name": "Lacha parantha", "price": 70, "description": "Veg Item. Lacha parantha. Costs: 70 rupees."}
    ],
    "Crispy Items": [
    {
        "name": "Crispy chicken",
        "options": [
            {"size": "half", "price": 400, "description": "Half portion"},
            {"size": "full", "price": 650, "description": "Full portion"}
        ]
    },
    {
        "name": "Chicken cheese balls",
        "options": [
            {"size": "half", "price": 250, "description": "Half portion"},
            {"size": "full", "price": 500, "description": "Full portion"}
        ]
    },
    {
        "name": "Chicken nuggets",
        "options": [
            {"size": "half", "price": 200, "description": "Half portion"},
            {"size": "full", "price": 400, "description": "Full portion"}
        ]
    },
    {
        "name": "Fish finger",
        "options": [
            {"size": "half", "price": 200, "description": "Half portion"},
            {"size": "full", "price": 400, "description": "Full portion"}
        ]
    }
],
    "Non Veg Pizza": [
    {
        "name": "Chicken blast",
        "options": [
            {"size": "small", "price": 250, "description": "Small size (e.g., 6-inch)"},
            {"size": "medium", "price": 400, "description": "Medium size (e.g., 8-inch)"},
            {"size": "large", "price": 550, "description": "Large size (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Peri peri chicken pizza",
        "options": [
            {"size": "small", "price": 250, "description": "Small size (e.g., 6-inch)"},
            {"size": "medium", "price": 400, "description": "Medium size (e.g., 8-inch)"},
            {"size": "large", "price": 550, "description": "Large size (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Roasted chicken pizza",
        "options": [
            {"size": "small", "price": 250, "description": "Small size (e.g., 6-inch)"},
            {"size": "medium", "price": 400, "description": "Medium size (e.g., 8-inch)"},
            {"size": "large", "price": 550, "description": "Large size (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Tandoori chicken pizza",
        "options": [
            {"size": "small", "price": 250, "description": "Small size (e.g., 6-inch)"},
            {"size": "medium", "price": 400, "description": "Medium size (e.g., 8-inch)"},
            {"size": "large", "price": 550, "description": "Large size (e.g., 12-inch)"}
        ]
    }
],
    "Veg Pizza": [
    {
        "name": "Paneer cheese pizza",
        "options": [
            {"size": "small", "price": 250, "description": "Small (e.g., 6-inch)"},
            {"size": "medium", "price": 400, "description": "Medium (e.g., 8-inch)"},
            {"size": "large", "price": 550, "description": "Large (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Mix veg pizza",
        "options": [
            {"size": "small", "price": 200, "description": "Small (e.g., 6-inch)"},
            {"size": "medium", "price": 350, "description": "Medium (e.g., 8-inch)"},
            {"size": "large", "price": 500, "description": "Large (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Tandoori veg pizza",
        "options": [
            {"size": "small", "price": 200, "description": "Small (e.g., 6-inch)"},
            {"size": "medium", "price": 350, "description": "Medium (e.g., 8-inch)"},
            {"size": "large", "price": 500, "description": "Large (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Mushroom veg pizza",
        "options": [
            {"size": "small", "price": 200, "description": "Small (e.g., 6-inch)"},
            {"size": "medium", "price": 350, "description": "Medium (e.g., 8-inch)"},
            {"size": "large", "price": 500, "description": "Large (e.g., 12-inch)"}
        ]
    },
    {
        "name": "Margherita veg pizza",
        "options": [
            {"size": "small", "price": 200, "description": "Small (e.g., 6-inch)"},
            {"size": "medium", "price": 350, "description": "Medium (e.g., 8-inch)"},
            {"size": "large", "price": 500, "description": "Large (e.g., 12-inch)"}
        ]
    }
],
    "Coffee": [
        {"name": "Cappuccino", "price": 70, "description": "Veg Item. Cappuccino. Costs: 70 rupees."},
        {"name": "Latte", "price": 70, "description": "Veg Item. Latte. Costs: 70 rupees."},
        {"name": "Black coffee", "price": 50, "description": "Veg Item. Black coffee. Costs: 50 rupees."},
        {"name": "Cold coffe with ice cream", "price": 120, "description": "Veg Item. Cold coffe with ice cream. Costs: 120 rupees."},
        {"name": "Hot chocolate", "price": 120, "description": "Veg Item. Hot chocolate. Costs: 120 rupees."}
    ],
    "Tea And Khawa": [
        {"name": "Milk tea", "price": 50, "description": "Veg Item. Milk tea. Costs: 50 rupees."},
        {"name": "Masala tea", "price": 50, "description": "Veg Item. Masala tea. Costs: 50 rupees."},
        {"name": "Lemon tea", "price": 50, "description": "Veg Item. Lemon tea. Costs: 50 rupees."},
        {"name": "Black tea", "price": 50, "description": "Veg Item. Black tea. Costs: 50 rupees."},
        {"name": "Kashmiri khawa", "price": 50, "description": "Veg Item. Kashmiri khawa. Costs: 50 rupees."}
    ],
    "Dessert": [
        {"name": "Brownie", "price": 90, "description": "Veg Item. Brownie. Costs: 90 rupees."},
        {"name": "Brownie with ice cream", "price": 150, "description": "Veg Item. Brownie with ice cream. Bestseller. Costs: 150 rupees."},
        {"name": "Chicken patty", "price": 50, "description": "Non-veg item. Chicken patty. Costs: 50 rupees."},
        {"name": "Mutton patty", "price": 60, "description": "Non-veg item. Mutton patty. Costs: 60 rupees."},
        {"name": "Plain cake", "price": 100, "description": "Veg Item. Plain cake. Costs: 100 rupees."},
        {"name": "Choclate cake", "price": 140, "description": "Veg Item. Choclate cake. Bestseller. Costs: 140 rupees."}
    ],
    "Shakes": [
        {"name": "Mango shake", "price": 120, "description": "Veg Item. Mango shake. Costs: 120 rupees."},
        {"name": "Banana shake", "price": 120, "description": "Veg Item. Banana shake. Costs: 120 rupees."},
        {"name": "Strawberry shake", "price": 120, "description": "Veg Item. Strawberry shake. Costs: 120 rupees."},
        {"name": "Oreo shake", "price": 120, "description": "Veg Item. Oreo shake. Costs: 120 rupees."},
        {"name": "Chocolate shake", "price": 120, "description": "Veg Item. Chocolate shake. Costs: 120 rupees."},
        {"name": "Vanilla shake", "price": 120, "description": "Veg Item. Vanilla shake. Costs: 120 rupees."},
        {"name": "Blackcurrant", "price": 120, "description": "Veg Item. Blackcurrant. Costs: 120 rupees."},
        {"name": "Butterscotch", "price": 120, "description": "Veg Item. Butterscotch. Costs: 120 rupees."},
        {"name": "Kikat shake", "price": 150, "description": "Veg Item. Kikat shake. Costs: 150 rupees."},
        {"name": "Almond shake", "price": 150, "description": "Veg Item. Almond shake. Costs: 150 rupees."},
        {"name": "Dates shake", "price": 150, "description": "Veg Item. Dates shake. Costs: 150 rupees."}
    ],
    "Mocktails": [
        {"name": "Green apple", "price": 120, "description": "Veg Item. Green apple. Costs: 120 rupees."},
        {"name": "Blueberry soda", "price": 120, "description": "Veg Item. Blueberry soda. Costs: 120 rupees."},
        {"name": "Strawberry soda", "price": 120, "description": "Veg Item. Strawberry soda. Costs: 120 rupees."},
        {"name": "Cranberry", "price": 120, "description": "Veg Item. Cranberry. Costs: 120 rupees."},
        {"name": "Virgin mojito", "price": 120, "description": "Veg Item. Virgin mojito. Costs: 120 rupees."},
        {"name": "Fresh lime water", "price": 80, "description": "Veg Item. Fresh lime water. Costs: 80 rupees."},
        {"name": "Fresh lime soda", "price": 80, "description": "Veg Item. Fresh lime soda. Costs: 80 rupees."}
    ],
    "Softy Scoop": [
        {"name": "Softy", "price": 60, "description": "Veg Item. Softy. Costs: 60 rupees."},
        {"name": "Vanilla", "price": 60, "description": "Veg Item. Vanilla. Costs: 60 rupees."},
        {"name": "Strawberry", "price": 70, "description": "Veg Item. Strawberry. Costs: 70 rupees."},
        {"name": "Mango", "price": 90, "description": "Veg Item. Mango. Costs: 90 rupees."},
        {"name": "American Nuts", "price": 90, "description": "Veg Item. American Nuts. Costs: 90 rupees."},
        {"name": "Kesar pista", "price": 90, "description": "Veg Item. Kesar pista. Bestseller. Costs: 90 rupees."},
        {"name": "Black Currant", "price": 90, "description": "Veg Item. Black Currant. Costs: 90 rupees."},
        {"name": "Dry fruit temptation", "price": 90, "description": "Veg Item. Dry fruit temptation. Costs: 90 rupees."},
	{"name": "oreo", "price": 90, "description": "Veg Item. Oreo. Costs: 90 rupees."},
	{"name": "Kashmir Matka Kulfi", "price": 70, "description": "Veg Item. Kashmir Matka Kulfi. Costs: 70 rupees."},
        {"name": "Mix ice vream bowl", "price": 180, "description": "Veg Item. Mix ice vream bowl. Costs: 180 rupees."}
    ]
}

def load_menu():
    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    if os.path.exists(menu_file):
        with open(menu_file, 'r') as f:
            return json.load(f)
    return DEFAULT_MENU

def save_menu(menu_data):
    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    with open(menu_file, 'w') as f:
        json.dump(menu_data, f, indent=2)

MENU = load_menu()

# Update the global availability dictionary from the menu:
for category, items in MENU.items():
    for item in items:
        AVAILABILITY[item['name']] = item.get('available', True)


# Initialize dish availability
def init_availability():
    global AVAILABILITY
    for category, items in MENU.items():
        for item in items:
            AVAILABILITY[item['name']] = True

init_availability()

def get_statistics():
    orders = load_orders()
    total_revenue = 0
    category_revenue = {}
    category_dish_count = {}
    daily_revenue = {}
    for date, day_data in orders.items():
        day_total = 0
        for order in day_data['orders']:
            if order.get('status') in ['paid', 'completed', 'payment complete']:
                total_revenue += order['total']
                day_total += order['total']
                for item in order['order_items']:
                    cat = item['category']
                    category_revenue[cat] = category_revenue.get(cat, 0) + (item['price'] * item['quantity'])
                    category_dish_count[cat] = category_dish_count.get(cat, 0) + item['quantity']
        daily_revenue[date] = day_total
    return {
        'total_revenue': total_revenue,
        'category_revenue': category_revenue,
        'category_dish_count': category_dish_count,
        'daily_revenue': daily_revenue
    }

ORDERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'orders.json')

def load_orders():
    if os.path.exists(ORDERS_FILE):
        try: #add a try catch block to catch json errors.
            with open(ORDERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {} #return empty dict if json is corrupt.
    return {}

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w') as f:
        json.dump(reviews, f, indent=2)

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# -------------------------
# Customer Routes
# -------------------------
@app.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = []
    return render_template('index.html', menu=MENU, fssai=FSSAI_LICENSE, availability=AVAILABILITY)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    category = request.form.get("category")
    item_name = request.form.get("item_name")
    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    selected_option = request.form.get("option", "")
    if selected_option and "|" in selected_option:
        size, price_str = selected_option.split("|")
        try:
            price = int(price_str)
        except ValueError:
            price = 0
    else:
        # For items without options, use default values from MENU
        size = "Regular"
        dish = next((i for i in MENU.get(category, []) if i["name"] == item_name), None)
        price = dish.get("price", 0) if dish else 0

    if price == 0:
        flash("Error: Price is invalid or 0.", "error")
        return redirect(url_for("index"))

    cart_item = {
        "category": category,
        "name": item_name,
        "quantity": quantity,
        "size": size,
        "price": price,
        "total": price * quantity,
        "option": selected_option
    }

    if "cart" not in session:
        session["cart"] = []
    
    updated = False
    for item in session["cart"]:
        if item["category"] == category and item["name"] == item_name and item.get("option") == selected_option:
            item["quantity"] += quantity
            item["total"] = item["price"] * item["quantity"]
            updated = True
            break

    if not updated:
        session["cart"].append(cart_item)
    
    session.modified = True

    flash(f"Added {quantity} x {item_name} ({size}) to cart!", "success")
    return redirect(url_for("index"))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total, fssai=FSSAI_LICENSE)

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        removed = cart.pop(index)
        session['cart'] = cart
        flash(f"Removed {removed['name']} from cart", "success")
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty!", "error")
        return redirect(url_for('index'))
    total = sum(item['price'] * item['quantity'] for item in cart)
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        dine_option = request.form.get('dine_option')
        table_number = request.form.get('table_number') if dine_option == 'eat_in' else None
        order_time = datetime.datetime.now().isoformat()
        today = get_today_date()
        orders = load_orders()
        if today not in orders:
            orders[today] = {'orders': []}
        used_numbers = {order['orderNumber'] for order in orders[today]['orders']}
        order_number = 1
        while order_number in used_numbers:
            order_number += 1
        order_data = {
            'orderNumber': order_number,
            'order_items': cart,
            'total': total,
            'paymentMethod': payment_method,
            'orderTime': order_time,
            'status': 'pending',  # Initially pending; will change to "payment complete" when confirmed
            'dine_option': dine_option,
            'table_number': table_number
        }
        orders[today]['orders'].append(order_data)
        save_orders(orders)
        session.pop('cart', None)
        if payment_method == 'online':
            qr_data = url_for('static', filename='images/QR.png')
            return render_template('payment.html', qr_data=qr_data, order=order_data, total=total, today=today, fssai=FSSAI_LICENSE)
        else:
            return render_template('order_confirmation.html', order=order_data, total=total, paymentMethod=payment_method, fssai=FSSAI_LICENSE)
    return render_template('checkout.html', cart=cart, total=total, fssai=FSSAI_LICENSE)
    
@app.route('/confirm_payment')
def confirm_payment():
    order_number = request.args.get('orderNumber')
    date = request.args.get('date')
    orders = load_orders()
    if date in orders:
        order = next((o for o in orders[date]['orders'] if str(o['orderNumber']) == str(order_number)), None)
        if order and order['paymentMethod'] == 'online':
            order['status'] = 'paid'
            save_orders(orders)
            return render_template('order_confirmation.html', order=order, total=order['total'], paymentMethod='online', fssai=FSSAI_LICENSE)
    return "Order not found or already processed."

# -------------------------
# Owner Routes
# -------------------------
@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Kifayat' and password == 'Muslimyouth':
            session['authenticated'] = True
            return redirect(url_for('owner_dashboard'))
        else:
            flash("Invalid credentials", "error")
    return render_template('login.html', fssai=FSSAI_LICENSE)

@app.route('/owner')
def owner_dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('owner_login'))
    orders = load_orders()
    stats = get_statistics()
    return render_template('owner.html', orders=orders, fssai=FSSAI_LICENSE, menu=MENU, availability=AVAILABILITY, stats=stats)

@app.route('/owner/complete_order', methods=['POST'])
def complete_order():
    date = request.form.get('date')
    orderNumber = request.form.get('orderNumber')
    orders = load_orders()
    if date in orders:
        for order in orders[date]['orders']:
            if str(order['orderNumber']) == str(orderNumber):
                order['status'] = 'completed'
                break
        save_orders(orders)
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/confirm_payment_received', methods=['POST'])
def confirm_payment_received():
    date = request.form.get('date')
    orderNumber = request.form.get('orderNumber')
    orders = load_orders()
    if date in orders:
        for order in orders[date]['orders']:
            if str(order['orderNumber']) == str(orderNumber):
                order['payment_confirmed'] = True
                order['status'] = 'payment complete'
                break
        save_orders(orders)
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/pricing', methods=['GET', 'POST'])
def pricing_availability():
    if not session.get('authenticated'):
        return redirect(url_for('owner_login'))
    global MENU, AVAILABILITY
    if request.method == 'POST':
        # Loop over each dish using a unique key: category__dishname
        for category, items in MENU.items():
            for item in items:
                dish_key = f"{category}__{item['name']}"
                new_price = request.form.get(f"price_{dish_key}")
                try:
                    new_price = float(new_price)
                except (ValueError, TypeError):
                    new_price = item['price']  # retain existing price if conversion fails
                item['price'] = new_price
                # Checkbox returns "on" if checked, else not present.
                available = request.form.get(f"available_{dish_key}")
                item['available'] = True if available == 'on' else False
                AVAILABILITY[item['name']] = item['available']
        save_menu(MENU)
        flash("Pricing and availability updated successfully.", "success")
        return redirect(url_for('owner_dashboard'))
    return render_template('pricing_availability.html', menu=MENU)


@app.route('/owner/toggle_availability', methods=['POST'])
def toggle_availability():
    dish = request.form.get('dish')
    if dish in AVAILABILITY:
        AVAILABILITY[dish] = not AVAILABILITY[dish]
        flash(f"Availability for {dish} set to {AVAILABILITY[dish]}", "success")
    else:
        flash("Dish not found", "error")
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/delete_order', methods=['POST'])
def delete_order():
    date = request.form.get('date')
    orderNumber = request.form.get('orderNumber')
    orders = load_orders()
    if date in orders:
        orders[date]['orders'] = [order for order in orders[date]['orders'] if str(order['orderNumber']) != str(orderNumber)]
        save_orders(orders)
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/logout')
def owner_logout():
    session.pop('authenticated', None)
    return redirect(url_for('owner_login'))

# -------------------------
# Review System Routes
# -------------------------
@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        name = request.form.get('name')
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        review_data = {
            'name': name,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.datetime.now().isoformat()
        }
        reviews = load_reviews()
        reviews.append(review_data)
        save_reviews(reviews)
        flash("Review submitted successfully!", "success")
        return redirect(url_for('index'))
    return render_template('review.html')

@app.route('/reviews')
def reviews():
    reviews = load_reviews()
    return render_template('reviews.html', reviews=reviews)

@app.route('/owner/reviews')
def owner_reviews():
    if not session.get('authenticated'):
        return redirect(url_for('owner_login'))
    reviews = load_reviews()
    return render_template('owner_reviews.html', reviews=reviews, fssai=FSSAI_LICENSE)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
