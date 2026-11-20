from typing import Annotated

from app.api.dependencies import CUSTOMER, require_role
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import Cart, CartItemCreate, CartQuantityUpdate
from app.services.cart_service import (
    CartConflict,
    CartError,
    CartForbidden,
    CartNotFound,
    CartService,
)
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/customers/{customer_id}/cart", tags=["cart"])

_ERROR_STATUS = {CartForbidden: 403, CartNotFound: 404, CartConflict: 409}

async def cart_error_response(request: Request, error: CartError) -> JSONResponse:
    return JSONResponse({"detail": str(error)}, status_code=_ERROR_STATUS[type(error)])

def get_cart_service() -> CartService:
    return CartService(CartRepository())

Customer = Annotated[dict, Depends(require_role(CUSTOMER))]
Service = Annotated[CartService, Depends(get_cart_service)]

@router.get("")
def get_cart(customer_id: str, response: Response, user: Customer, service: Service) -> Cart:
    response.headers["Cache-Control"] = "no-store"
    return service.get_or_create(customer_id, user)

@router.post("/items")
def add_item(
    customer_id: str, request: CartItemCreate, user: Customer, service: Service
) -> Cart:
    return service.add(customer_id, user, request)

@router.patch("/items/{item_id}")
def update_item(
    customer_id: str,
    item_id: str,
    request: CartQuantityUpdate,
    user: Customer,
    service: Service,
) -> Cart:
    return service.update_quantity(customer_id, user, item_id, request)

@router.delete("/items/{item_id}")
def remove_item(customer_id: str, item_id: str, user: Customer, service: Service) -> Cart:
    return service.remove(customer_id, user, item_id)

@router.delete("/items")
def clear_cart(customer_id: str, user: Customer, service: Service) -> Cart:
    return service.clear(customer_id, user)
