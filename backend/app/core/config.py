
"""
Central configuration for backend data file locations.

These paths are used by the repository layer to read and
write restaurant and menu information stored in JSON files.
"""


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