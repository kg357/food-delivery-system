
"""
Central configuration for backend data file locations.

These paths are used by the repository layer to read and
write restaurant and menu information stored in JSON files.
"""


import os
from pathlib import Path


# ============================================================
# Project Directories
# ============================================================

# __file__ is the location of this config.py file.
# resolve() converts it to an absolute path.
# Moving up three parent directories gives the backend folder.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# The data directory is located directly inside backend/.
DATA_DIR = BASE_DIR / "data"


# ============================================================
# JSON Data Files
# ============================================================

# Restaurant records, including details and ownership information.
RESTAURANTS_FILE = DATA_DIR / "restaurants.json"

# Menu item records associated with restaurants.
MENU_ITEMS_FILE = DATA_DIR / "menu_items.json"

# Order records, including customer information and order details.
ORDERS_FILE = DATA_DIR / "orders.json"
# Customer and staff accounts, including hashed passwords.
CUSTOMERS_FILE = DATA_DIR / "customers.json"


# ============================================================
# Authentication Settings
# ============================================================

# Secret used to sign login tokens. Anyone who knows it can forge a
# token, so real deployments must set the JWT_SECRET environment
# variable. The default below only exists so the project runs locally.
JWT_SECRET = os.environ.get(
    "JWT_SECRET",
    "development-only-secret-change-before-deploying",
)

# HS256 signs and verifies tokens with the same secret.
JWT_ALGORITHM = "HS256"

# How long a login token stays valid, in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 60
