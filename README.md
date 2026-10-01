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

## Start the Application

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
