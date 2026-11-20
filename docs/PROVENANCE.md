# Generative AI Use and Provenance

This is the team's shared record of AI contributions to project artifacts. Add an entry when AI output affects work that becomes part of the project.

## Entry 1 — User story issue template

- Student(s): Kiran Grewal
- Artifact: `.github/ISSUE_TEMPLATE/user_story.md`
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Draft a consistent template for user story issues.
- Influence: Used and adapted the generated template.
- Validation: Compared the template's user story statement and acceptance criteria sections with the lecture slides.
- PR or commit: PR #6

## Entry 2 — Backend CI workflow

- Student(s): Kiran Grewal
- Artifact: `.github/workflows/backend-tests.yml`
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Set up automated backend tests for pull requests to `main`.
- Influence: Used and adapted the generated GitHub Actions workflow.
- Validation: GitHub Actions ran `python -m pytest` on PR #8; 7 tests passed.
- PR or commit: PR #8

## Entry 3 — Menu browsing backend (B1.2-B1.5)

- Student(s): Aleem Shaik
- Artifact: `backend/data/menu_items.json` (seed data), `backend/app/repositories/menu_repository.py` (`load_menu_items_by_restaurant`), `backend/app/services/menu_service.py` (`get_menu_for_restaurant`), `backend/app/api/routes/menu.py` (`GET /restaurants/{restaurant_id}/menu`), `backend/tests/test_menu_browse.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Generate the seed menu data, the browse-menu endpoint (repository, service and route layers) and its tests.
- Influence: Helped with code generation. I chose the tasks and the layered structure to match the team's existing code, reviewed each layer with the AI explaining it line by line.
- Validation: Ran `python3 -m pytest` locally (87 passed at that point); GitHub Actions passed on the PR.
- PR or commit: PR #93

## Entry 4 — Menu item details backend (B2.1-B2.3)

- Student(s): Aleem Shaik
- Artifact: `backend/app/repositories/menu_repository.py` (`load_menu_item_by_id`), `backend/app/services/menu_service.py` (`get_menu_item_for_restaurant`), `backend/app/api/routes/menu.py` (`GET /restaurants/{restaurant_id}/menu/{item_id}`), `backend/tests/test_menu_item_details.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Generate the endpoint that returns one menu item, with 404 handling for a missing restaurant or item, and its tests.
- Influence: Helped with code generation and testing. I reviewed each layer with the AI explaining it line by line to understand thoroughly how everything works.
- Validation: Ran `python3 -m pytest` locally (98 passed); GitHub Actions passed on the PR.
- PR or commit: PR #96

## Entry 5 — Menu browsing and menu item details frontend (B1.6-B1.8, B2.4-B2.5)

- Student(s): Aleem Shaik
- Artifact: `frontend/src/api/menu.js` (`getMenu`, `getMenuItem`), `frontend/src/components/MenuList/`, `frontend/src/pages/MenuItemDetails/`, route added in `frontend/src/App.jsx`, `frontend/src/pages/RestaurantDetails/RestaurantDetails.jsx` (placeholder replaced by `MenuList`), `frontend/src/tests/MenuList.test.jsx`, `frontend/src/tests/MenuItemDetails.test.jsx`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Generate the menu list and menu item details UI (loading, error and empty states) and the frontend tests for them.
- Influence: Helped with code generation, following the structure and style of the team's existing frontend. I reviewed the result, ran the app and tests which the AI helped with.
- Validation: `npx vitest run` passes all 13 new tests (the 2 failures in `App.test.jsx` are pre-existing and unrelated); manually checked in the browser: restaurant page, menu list, item details, back link.
- PR or commit: PR #100

## Entry 6 — Backend organization and documentation
- Student(s): Trinity Bell
- Artifact: backend/tests/ (reorganized into repository/, routes/, service/, and schemas_identifiers/), backend/app/core, backend/app/schemas/, backend/app/repositories/, backend/app/services/, backend/app/api/routes/, backend/app/main.py
- Label: AI-GENERATED
- AI Tool: ChatGPT
- Purpose: Reorganize and consolidate backend tests into route, service, and repository; standardize formatting; add comments to make the repository easier to understand.
- Influence: Quickly reorganize code into a standardized formatting and add comments. I manually reviewed each edit and added them myself in VS Code. 
- Validation: Ran python -m pytest locally after every change to verify no functionality was lost. 
- PR or commit: 

## Entry 7 — Authentication stub (E2.13)

- Student(s): Aleem Shaik
- Artifact: `backend/app/api/dependencies.py` (`get_current_user`, `require_role`), `backend/tests/routes/test_auth_dependencies.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Generate a temporary `get_current_user` dependency (returns a fixed fake customer) and a `require_role` dependency, so teammates can build cart, checkout and order routes before real authentication exists, plus tests for both.
- Influence: Helped with code generation. I created the issue and branch, chose the contract the team shares (`{id, role, active}`) and ran the tests; the AI explained how FastAPI dependencies work.
- Validation: Ran `python -m pytest` locally (135 passed); GitHub Actions to confirm on the pull request.
- PR or commit: Closes issue #147

## Entry 8 — Shopping cart backend tests

- Student(s): Kiran Grewal
- Artifact: test_cart_routes, test_cart_service
- Label: AI-GENERATED
- AI tool: OpenAI Codex
- Purpose: Aided with the the tests for the route and service layer
- Influence: Codex tested the cart changes using the team's JSON storage and shared identity dependency.
- Validation: Ran the backend pytest suite. Test counts are recorded in the pull request.

## Entry 9 — Shopping cart backend

- Student(s): Kiran Grewal
- Artifact: services/cart_service.py, api/routes/cart.py
- Label: AI-ASSISTED
- AI tool: OpenAI Codex
- Purpose: Assisted with the service and route layer, providing ideas and explanations.
- Influence: Service logic, FAST API endpoints
- Validation: Ran the backend pytest suite. Test counts are recorded in the pull request.
## Entry 10 — Customer accounts and authentication backend (E1.1-E1.13, E2.1-E2.9)

- Student(s): Aleem Shaik
- Artifact: `backend/app/core/security.py`, `backend/app/core/roles.py`, `backend/app/core/config.py`, `backend/app/core/identifiers.py` (`generate_customer_id`), `backend/app/schemas/customer.py`, `backend/app/schemas/auth.py`, `backend/app/repositories/customer_repository.py`, `backend/app/services/customer_service.py`, `backend/app/services/auth_service.py`, `backend/app/api/routes/customers.py`, `backend/app/api/routes/auth.py`, `backend/app/api/dependencies.py` (real `get_current_user`), `backend/app/api/routes/restaurants.py` (owner from the token), `backend/data/customers.json` (demo accounts), `backend/requirements.txt` (`bcrypt`, `PyJWT`), and the new tests under `backend/tests/`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Generate customer registration, retrieval, update and deactivation, bcrypt password hashing, JWT login, the real `get_current_user`, role and ownership checks, and replacing the hard-coded `development_owner` in the restaurant routes, plus tests for all of it.
- Influence: Helped with code generation, following the structure and style of the team's existing route / service / repository layers. I chose the plan (JWT with bcrypt, the endpoint paths, 401 versus 403, deactivation keeps the record), reviewed each layer with the AI explaining it, and ran the tests.
- Validation: `python -m pytest` passes locally (229 passed). Logged in as the demo owner and admin accounts against the real data file. GitHub Actions to confirm on the pull request.
- PR or commit: Closes issues #145, #146 and their tasks E1.1-E1.13 and E2.1-E2.9
