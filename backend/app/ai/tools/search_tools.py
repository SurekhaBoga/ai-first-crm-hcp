"""Deterministic execution for the search_interaction intent."""

from sqlalchemy.orm import Session

from app.ai.schemas.search import InteractionSearchFilters
from app.ai.tools.coercion import coerce_date, coerce_interaction_type, coerce_sentiment
from app.models.interaction import Interaction
from app.services import doctor_service, interaction_service


def search_interactions_tool(
    db: Session, filters: InteractionSearchFilters, *, page: int = 1, page_size: int = 20
) -> tuple[list[Interaction], int]:
    doctor_id = None
    if filters.doctor_name:
        matches, total_matches = doctor_service.search_doctors(db, filters.doctor_name, page=1, page_size=5)
        if total_matches == 0:
            return [], 0  # no matching doctor -> no results, not an error
        doctor_id = matches[0].id

    # There's no Product table or full-text index in this backend
    # foundation, so `product`/`keyword` can't be pushed into the SQL
    # WHERE clause. Everything the DB *can* filter on (doctor, type,
    # sentiment, date range) is filtered there; product/keyword are
    # applied as an in-memory pass over that (capped) result set, and
    # pagination happens after.
    db_items, _ = interaction_service.list_interactions(
        db,
        page=1,
        page_size=500,
        doctor_id=doctor_id,
        interaction_type=coerce_interaction_type(filters.interaction_type),
        sentiment=coerce_sentiment(filters.sentiment),
        date_from=coerce_date(filters.date_from, field_name="date_from"),
        date_to=coerce_date(filters.date_to, field_name="date_to"),
    )

    items = db_items
    if filters.product:
        needle = filters.product.lower()
        items = [i for i in items if any(needle in p.lower() for p in i.products_discussed)]
    if filters.keyword:
        needle = filters.keyword.lower()
        items = [
            i
            for i in items
            if needle in (i.discussion_points or "").lower() or needle in (i.purpose or "").lower()
        ]

    total = len(items)
    start = (page - 1) * page_size
    return items[start : start + page_size], total
