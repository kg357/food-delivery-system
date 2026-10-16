# Food Delivery System

## Team Name 

Thinkers

## Requirements
Python 3.14.7

## Setup

Clone the repository:

```bash
git clone https://github.com/kg357/food-delivery-system.git

cd food-delivery-system

cd backend
```

## Virtual Environment

Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

With the virtual environment activated, install the project dependencies:

```bash
pip install -r requirements.txt
```

## Start the Backend 

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The application will start at:
`http://127.0.0.1:8000`

## API Endpoints

**GET `/health`**

Return HTTP 200:

```json
{
    "status": "ok"
}
```

**GET `/restaurants`**

Returns the list of representative restaurants, e.g.:

```json
[
    {"id": 1, "name": "Wasabi Ramen", "cuisine": "Japanese", "rating": 4.5, "address": "123 Main St"}
]
```

**GET `/restaurants/{restaurant_id}/menu`**

Returns every menu item that belongs to the given restaurant, including items marked unavailable. Returns an empty list if the restaurant has no items. Returns HTTP 404 (`{"detail": "Restaurant not found"}`) if the restaurant does not exist, and HTTP 422 if `restaurant_id` is not an integer. E.g.:

```json
[
    {
        "id": "3f1c2a9e-5b7d-4e21-9c0a-8d6e4b1f2a77",
        "restaurant_id": 1,
        "name": "Tonkotsu Ramen",
        "description": "Pork broth with noodles",
        "price": 14.5,
        "available": true
    }
]
```

**GET `/restaurants/{restaurant_id}/menu/{item_id}`**

Returns a single menu item (same shape as above). Returns HTTP 404 with `{"detail": "Restaurant not found"}` if the restaurant does not exist, or `{"detail": "Menu item not found"}` if the item does not exist or belongs to a different restaurant.

## API Documentation

Interactive docs (Swagger UI) are available at:
`http://127.0.0.1:8000/docs`

## Representative Data

Representative restaurant data lives at `backend/data/restaurants.json`.

## Running Tests
```bash
python3 -m pytest
```

Covers the health endpoint, the restaurant-list endpoint, repository behavior (using isolated temporary test data, never the committed data file), and at least one invalid-data failure case.

The menu endpoints are covered by `tests/test_menu_browse.py` and `tests/test_menu_item_details.py`.

Frontend tests (from the `frontend` directory):

```bash
npx vitest run
```

The menu list and menu item details pages are covered by `src/tests/MenuList.test.jsx` and `src/tests/MenuItemDetails.test.jsx`.



## Frontend Setup

The frontend uses React and Vite.

### Requirements
- Node.js
- npm

### Install Dependencies

From the repository root:

```bash
cd frontend
npm install
npm run dev


## Repository Structure

```text
food-delivery-system/
|-- .gitignore
├── .github/
│   └── ISSUE_TEMPLATE/
│       └── user_story.md
|-- README.md
|-- backend/
    |-- app/
    |   |-- api/routes/       # HTTP route definitions
    |   |-- services/         # Business logic
    |   |-- repositories/     # Data access (reads from JSON)
    |   |-- schemas/          # 
    team agreement
    ├   ├-- scrum/
    │        └── team-agreement.md 
    Pydantic models
    |   |-- core/             # Configuration (file paths)
    |   |-- main.py
    |-- data/                 # Representative JSON data
    |-- tests/
    |-- requirements.txt
```
