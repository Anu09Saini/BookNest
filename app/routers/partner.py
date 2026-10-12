from fastapi import APIRouter, Depends

from app.dependencies.partner_auth import get_current_partner
from app.schemas.book import BookListItem
from app.services.book_service import get_all_books


router = APIRouter(
  prefix="/partner",
  tags=["Partner API"],
)


@router.get( "/catalogue/books", response_model=list[BookListItem],)
def partner_book_catalogue(partner: dict = Depends(get_current_partner),):
  return get_all_books()
