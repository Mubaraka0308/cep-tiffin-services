from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import MenuItem, Provider, User
from backend.schemas import MenuItemCreate, MenuItemUpdate, MenuItemOut
from backend.auth_utils import require_role

router = APIRouter(tags=["Menu Management"])


@router.get("/api/providers/{provider_id}/menu", response_model=List[MenuItemOut])
def get_provider_menu(provider_id: int, db: Session = Depends(get_db)):
    """
    Returns the list of menu items for a given provider.
    Accessible by both students and providers.
    """
    items = db.query(MenuItem).filter(MenuItem.provider_id == provider_id).all()
    return items


@router.post("/api/providers/menu", response_model=MenuItemOut)
def add_menu_item(
    payload: MenuItemCreate,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Allows a provider to add a dish/thali to their menu.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    new_item = MenuItem(
        provider_id=provider.id,
        name=payload.name,
        description=payload.description,
        meal_type=payload.meal_type,
        category=payload.category,
        price=payload.price,
        is_available=payload.is_available
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.put("/api/menu/{item_id}", response_model=MenuItemOut)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Update an existing menu item. Ensures a provider can only modify their own items.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    item = db.query(MenuItem).filter(
        MenuItem.id == item_id,
        MenuItem.provider_id == provider.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found or unauthorized.")

    for field, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(item, field, val)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/api/menu/{item_id}")
def delete_menu_item(
    item_id: int,
    current_user: User = Depends(require_role("provider")),
    db: Session = Depends(get_db)
):
    """
    Delete a menu item from the provider's active menu.
    """
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found.")

    item = db.query(MenuItem).filter(
        MenuItem.id == item_id,
        MenuItem.provider_id == provider.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found or unauthorized.")

    db.delete(item)
    db.commit()
    return {"message": f"Menu item '{item.name}' deleted successfully."}
