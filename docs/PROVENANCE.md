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
