# Food Delivery System

**Team:** Thinkers
**Requirements:** Python 3.14.7

## Implemented Features
### Customer Features
- Browse available restaurants.
- Search restaurants by name through the frontend.
- Filter restaurants by cuisine and minimum rating.
- View detailed information about a restaurant.
- Browse a restaurant's menu, including item availability.
- View individual menu item details.
- Navigate between restaurant listings, restaurant details, and menu items.

### Restaurant Owner Features
- Access the restaurant owner interface.
- View restaurants associated with their ownerID.
- Create new restaurants.
- Update restaurant names, cuisines, and addresses.
- Add menu items to restaurants.
- Edit existing menu items, including their price, description, and availability.

### Administrative Features
An administrator demonstration entry point is included, but administrative functionality has not yet been implemented.

### Current Scope and Limitations
- **Authentication:** Real authentication and account management have not been implemented. Demonstration roles are used for frontend navigation.
- **Restaurant & menu ownership:** Restaurant & menu creation and editing currently use the fixed development owner ID `development_owner`.
- **Ordering and payments:** Customer ordering, checkout, payments, and delivery tracking are outside the current implementation.

## Prerequisites
Install the following before running the project:
- Python 3.14.7
- Node.js and npm
- Git

## Installation and Setup
### 1. Clone the Repository
Open a terminal and run:
```bash
git clone https://github.com/kg357/food-delivery-system.git
cd food-delivery-system
```

### 2. Configure the Backend
Navigate to the backend directory:
```bash
cd backend
```

Create a Python virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment.
**Windows (PowerShell):**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
**macOS / Linux:**
    ```bash
    source .venv/bin/activate
    ```

Install the backend dependencies:
```bash
python -m pip install -r requirements.txt
```

Start the backend server:
```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at:
`http://localhost:8000`

To verify that the backend is running, visit:
`http://localhost:8000/health`

Expected response:
```json
{
  "status": "OK"
}
```

Make sure to leave the backend server running while starting the frontend.

### 3. Configure the Frontend
Open a new terminal. 
From the repository root, navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the frontend development server:
```bash
npm run dev
```

The frontend will normally be available at:
`http://localhost:5173` // If yours opens on a different port (e.g. 5174), use that.
Open this address in your browser to access the application.

**Important:** Both the backend and frontend servers must be running for the application to work correctly.

## Backend Architecture
The backend follows a layered architecture:
```text
HTTP Request
     |
     v
API Route
     |
     v
Service Layer
     |
     v
Repository Layer
     |
     v
JSON Data Files
```

### API Routes
Located in `backend/app/api/routes/`.
Routes define HTTP endpoints, receive requests, validate inputs using Pydantic schemas, and return HTTP responses.

### Service Layer
Located in `backend/app/services/`.
Services implement business rules, such as restaurant filtering, restaurant creation, ownership verification, and checking whether restaurants or menu items exist.

### Repository Layer
Located in `backend/app/repositories/`.
Repositories handle reading and writing restaurant and menu data stored in JSON files.

### Schemas
Located in `backend/app/schemas/`.
Pydantic schemas define the structure and validation requirements for restaurant and menu-item data.
This separation helps keep the application maintainable, testable, and easier to extend.

## API Endpoints
The backend exposes nine endpoints.

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Confirm the backend is responding |

### Restaurants
| Method | Endpoint | Description |
|---|---|---|
| GET | `/restaurants` | Retrieve restaurants with optional filters |
| GET | `/restaurants/{restaurant_id}` | Retrieve restaurant details |
| POST | `/restaurants` | Create a restaurant |
| PATCH | `/restaurants/{restaurant_id}` | Update an existing restaurant |

The restaurant-list endpoint supports the following optional query parameters:
| Parameter | Description |
|---|---|
| `cuisine` | Filter by cuisine, case-insensitively |
| `min_rating` | Minimum rating between 0 and 5, inclusive |

Example request:
```text
GET /restaurants?cuisine=Italian&min_rating=4
```

### Menu Items
| Method | Endpoint | Description |
|---|---|---|
| GET | `/restaurants/{restaurant_id}/menu` | Retrieve a restaurant's menu |
| GET | `/restaurants/{restaurant_id}/menu/{item_id}` | Retrieve an individual menu item |
| POST | `/restaurants/{restaurant_id}/menu` | Create a menu item |
| PATCH | `/restaurants/{restaurant_id}/menu/{item_id}` | Update a menu item |

Menu retrieval includes both available and unavailable items.
An existing restaurant with no menu items returns an empty list.

### HTTP Status Codes
| Code | Meaning |
|---|---|
| 200 | Request completed successfully |
| 201 | Resource created successfully |
| 403 | Supplied owner ID does not match the restaurant owner |
| 404 | Requested restaurant or menu item was not found |
| 422 | Request parameters or body failed validation |

Menu update requests ignore omitted fields and fields explicitly set to `null`. Restaurant update requests reject explicitly supplied `null` values for editable fields.

### Interactive API Documentation
FastAPI automatically generates API documentation using OpenAPI.
Swagger UI:
http://localhost:8000/docs

OpenAPI JSON specification:
http://localhost:8000/openapi.json

The Swagger interface can be used to inspect request schemas, execute endpoints, and view responses without using the React frontend.

## Data Persistence
The backend stores representative data in:
```text
backend/data/restaurants.json
backend/data/menu_items.json
```

Restaurant records contain:
- Restaurant ID
- Owner ID
- Name
- Cuisine
- Rating
- Address

Menu-item records contain:
- Menu item ID
- Restaurant ID
- Name
- Description
- Price
- Availability

Restaurant IDs are generated as unused positive integers. Menu item IDs are generated using UUIDs.
The repository writes updated records back to JSON so that changes persist between application restarts.

## Automated Testing
The project includes automated backend and frontend tests.

### Backend Tests
From the `backend` directory, activate the virtual environment and run:
```bash
python -m pytest
```

For detailed output:
```bash
python -m pytest -v
```

Backend tests are organized by architectural layer:
```text
backend/tests/
├── conftest.py
├── repository/
│   ├── test_restaurant_repository.py
│   └── test_menu_repository.py
├── service/
│   ├── test_restaurant_service.py
│   └── test_menu_service.py
├── routes/
│   ├── test_health_routes.py
│   ├── test_restaurant_routes.py
│   └── test_menu_routes.py
└── schemas_identifiers/
    ├── test_restaurant_schemas.py
    └── test_identifiers.py
```

The tests cover:
- Health-check responses.
- Restaurant retrieval and filtering.
- Restaurant creation and updates.
- Restaurant ownership checks.
- Menu-item creation, retrieval, and updates.
- Repository JSON persistence.
- Request validation and invalid-data scenarios.
- Missing restaurants and menu items.

Shared fixtures are defined in `conftest.py`.

Repository and service tests use temporary JSON files where appropriate, preventing test operations from modifying the committed development data.

### Frontend Tests
From the `frontend` directory, run:
```bash
npx vitest run
```
The frontend test suite includes tests for menu browsing and individual menu-item details, including loading, error, and empty states.

For example:
```text
frontend/src/tests/MenuList.test.jsx
frontend/src/tests/MenuItemDetails.test.jsx
```

### Production Build
From the `frontend` directory, verify that the frontend builds successfully:
```bash
npm run build
```

## Repository Structure
```text
food-delivery-system/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── user_story.md
│   └── workflows/
│       └── backend-tests.yml
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── menu.py
│   │   │       └── restaurants.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── identifiers.py
│   │   ├── repositories/
│   │   │   ├── menu_repository.py
│   │   │   └── restaurant_repository.py
│   │   ├── schemas/
│   │   │   ├── menu_item.py
│   │   │   └── restaurant.py
│   │   ├── scrum/
│   │   │   ├── 09-29-lab-minutes.md
│   │   │   ├── 10-01-meeting-minutes.md
│   │   │   ├── 10-06-lab-minutes.md
│   │   │   ├── 10-13-lab-minutes.md
│   │   │   └── team-agreement.md
│   │   ├── services/
│   │   │   ├── menu_service.py
│   │   │   └── restaurant_service.py
│   │   └── main.py
│   ├── data/
│   │   ├── menu_items.json
│   │   └── restaurants.json
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── repository/
│   │   ├── routes/
│   │   ├── schemas_identifiers/
│   │   └── service/
│   ├── pytest.ini
│   └── requirements.txt
├── docs/
│   └── PROVENANCE.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── tests/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── App.test.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .gitignore
└── README.md
```
