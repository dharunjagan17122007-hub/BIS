from fastapi import APIRouter, Query, Depends
import re
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Standard
from app.services.recommendation_service import recommend_standards

router = APIRouter(
    prefix="/api/standards",
    tags=["BIS Standards"]
)

@router.get("/search")
def search_standards(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    query = query.strip()
    search_query = query.lower()

    # Remove common question words
    stop_words = {
        "what", "which", "is", "the", "for", "a", "an",
        "of", "to", "used", "use", "standard", "bis",
        "does", "cover", "covers", "specifies", "specify",
        "should", "i", "need", "do", "we"
    }

    words = re.findall(r"\b[a-zA-Z0-9]+\b", search_query)
    keywords = [word for word in words if word not in stop_words]

    standards = db.query(Standard).all()
    scored_results = []

    for standard in standards:
        is_number = standard.is_number.lower()
        title = standard.title.lower()
        category = standard.category.lower()
        description = (standard.description or "").lower()

        score = 0

        # Exact IS number
        if search_query == is_number:
            score += 100

        # Match individual keywords
        for keyword in keywords:
            if keyword in is_number:
                score += 80

            if keyword in title:
                score += 50

            if keyword in category:
                score += 30

            if keyword in description:
                score += 20

        if score > 0:
            scored_results.append((score, standard))

    # Best matches first
    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return {
        "query": query,
        "count": len(scored_results),
        "results": [
            {
                "id": standard.id,
                "is_number": standard.is_number,
                "title": standard.title,
                "category": standard.category,
                "description": standard.description,
                "status": standard.status,
                "relevance_score": score
            }
            for score, standard in scored_results
        ]
    }
@router.get("/recommend")
def recommend(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    query = query.strip()

    standards = db.query(Standard).all()

    results = recommend_standards(
        query=query,
        standards=standards,
        limit=5
    )

    return {
        "query": query,
        "count": len(results),
        "recommendations": results
    }

@router.get("/{is_number:path}")
def get_standard(
    is_number: str,
    db: Session = Depends(get_db)
):
    standard = db.query(Standard).filter(
        Standard.is_number.ilike(is_number.strip())
    ).first()

    if standard:
        return {
            "found": True,
            "standard": {
                "id": standard.id,
                "is_number": standard.is_number,
                "title": standard.title,
                "category": standard.category,
                "description": standard.description,
                "status": standard.status
            }
        }

    return {
        "found": False,
        "message": "Standard not found"
    }
    
