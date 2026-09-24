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

## Running Tests
``` bash
pytest
```

## Repository Structure

```text
food-delivery-system/
|-- .gitignore
|-- README.md
|-- backend/
    |-- app/
    |   |-- api/
    |   |   |-- routes/
    |   |-- main.py
    |-- tests/
    |-- requirements.txt
```