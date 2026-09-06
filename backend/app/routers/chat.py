from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
import re

from app.database import get_db
from app.models import Standard
from app.services.recommendation_service import recommend_standards


router = APIRouter(
    prefix="/api/chat",
    tags=["BIS Chat Assistant"]
)


# =========================================================
# EXTRACT IS NUMBER
# =========================================================

def extract_is_number(query: str):
    """
    Detect an IS number from user input.

    Examples:
    IS 456
    IS 1786
    IS 10500
    IS 800:2007
    """

    match = re.search(
        r"\bIS\s*\d+(?:\s*\([^)]*\))?(?::\d{4})?",
        query,
        re.IGNORECASE
    )

    if match:
        return match.group(0).strip()

    return None


# =========================================================
# FIND STANDARD BY IS NUMBER
# =========================================================

def find_standard_by_is_number(
    db: Session,
    is_number: str
):
    """
    Find a standard using its IS number.
    """

    normalized = re.sub(
        r"\s+",
        " ",
        is_number.strip().lower()
    )

    standards = db.query(Standard).all()

    for standard in standards:

        standard_number = re.sub(
            r"\s+",
            " ",
            standard.is_number.strip().lower()
        )

        if standard_number == normalized:
            return standard

    return None


# =========================================================
# CONVERT STANDARD TO DICTIONARY
# =========================================================

def standard_to_dict(standard: Standard):
    """
    Convert database Standard object
    into a JSON-friendly dictionary.
    """

    return {
        "is_number": standard.is_number,
        "title": standard.title,
        "category": standard.category,
        "description": standard.description,
        "status": standard.status,
        "source_url": standard.source_url
    }


# =========================================================
# DETECT EXPLICIT CATEGORY REQUEST
# =========================================================

def detect_category(query: str):
    """
    Detect category only when the user explicitly
    asks for a category of standards.

    This prevents queries such as:
    'I manufacture steel reinforcement bars'

    from being treated as a general category search.
    """

    text = query.lower().strip()

    category_patterns = {

        "Construction": [
            "construction standards",
            "construction standard",
            "construction category",
            "standards for construction",
            "standards in construction",
            "show construction standards",
            "list construction standards"
        ],

        "Electrical": [
            "electrical standards",
            "electrical standard",
            "electrical category",
            "standards for electrical",
            "standards in electrical",
            "show electrical standards",
            "list electrical standards"
        ],

        "Food & Agriculture": [
            "food standards",
            "food standard",
            "food category",
            "agriculture standards",
            "agriculture standard",
            "agriculture category",
            "standards for food",
            "standards for agriculture"
        ],

        "Water & Environment": [
            "water standards",
            "water standard",
            "water category",
            "environment standards",
            "environment standard",
            "environment category",
            "standards for water",
            "standards for environment"
        ],

        "Mechanical & Manufacturing": [
            "mechanical standards",
            "mechanical standard",
            "mechanical category",
            "manufacturing standards",
            "manufacturing standard",
            "manufacturing category",
            "standards for manufacturing",
            "standards for mechanical"
        ],

        "Textiles": [
            "textile standards",
            "textile standard",
            "textiles standards",
            "textiles standard",
            "textile category",
            "standards for textile",
            "standards for textiles"
        ]
    }

    for category, patterns in category_patterns.items():

        for pattern in patterns:

            if pattern in text:
                return category

    return None


# =========================================================
# CREATE ASSISTANT-STYLE RECOMMENDATION ANSWER
# =========================================================

def create_recommendation_answer(
    best_match: dict,
    related_standards: list
):
    """
    Create a human-readable response
    for the recommended BIS standard.
    """

    is_number = best_match["is_number"]
    title = best_match["title"]
    description = best_match.get("description") or ""
    category = best_match["category"]
    status = best_match["status"]

    explanation = description.strip().rstrip(".")

    answer = (
        f"Recommended BIS Standard\n\n"
        f"{is_number}\n"
        f"{title}\n\n"
        f"Why this standard?\n"
        f"This standard specifically covers "
        f"{explanation.lower()}.\n\n"
        f"Category:\n"
        f"{category}\n\n"
        f"Status:\n"
        f"{status}"
    )

    if related_standards:

        answer += "\n\nRelated Standards\n"

        for standard in related_standards:

            answer += (
                f"• {standard['is_number']} — "
                f"{standard['title']}\n"
            )

    return answer


# =========================================================
# CHAT ASSISTANT ENDPOINT
# =========================================================

@router.get("/")
def chat(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):

    query = query.strip()

    # =====================================================
    # 1. DIRECT IS NUMBER LOOKUP
    # =====================================================

    is_number = extract_is_number(query)

    if is_number:

        standard = find_standard_by_is_number(
            db,
            is_number
        )

        if standard:

            return {
                "query": query,
                "found": True,
                "response_type": "standard_lookup",
                "answer": (
                    f"{standard.is_number}: "
                    f"{standard.title}"
                ),
                "standard": standard_to_dict(
                    standard
                )
            }


    # =====================================================
    # 2. EXPLICIT CATEGORY SEARCH
    # =====================================================

    category = detect_category(query)

    if category:

        standards = (
            db.query(Standard)
            .filter(
                Standard.category == category
            )
            .limit(10)
            .all()
        )

        return {
            "query": query,
            "found": len(standards) > 0,
            "response_type": "category_search",
            "category": category,
            "answer": (
                f"I found {len(standards)} BIS standards "
                f"related to {category}."
            ),
            "standards": [
                standard_to_dict(standard)
                for standard in standards
            ]
        }


    # =====================================================
    # 3. NATURAL-LANGUAGE RECOMMENDATION
    # =====================================================

    all_standards = db.query(Standard).all()

    recommendations = recommend_standards(
        query,
        all_standards,
        limit=5
    )

    if recommendations:

        # First result = best recommendation
        best_match = recommendations[0]

        # Remaining results = related standards
        related_standards = recommendations[1:]

        # Create readable assistant response
        answer = create_recommendation_answer(
            best_match,
            related_standards
        )

        # =================================================
        # CLEAN JSON RESPONSE
        # =================================================

        return {
            "query": query,
            "found": True,
            "response_type": "recommendation",

            "answer": answer,

            "best_match": {
                "is_number": best_match["is_number"],
                "title": best_match["title"],
                "category": best_match["category"],
                "status": best_match["status"],
                "reason": best_match["reason"]
            },

            "related_standards": [
                {
                    "is_number": standard["is_number"],
                    "title": standard["title"]
                }
                for standard in related_standards
            ]
        }


    # =====================================================
    # 4. NO MATCH
    # =====================================================

    return {
        "query": query,
        "found": False,
        "response_type": "no_match",
        "answer": (
            "I could not identify a matching BIS standard "
            "for your requirement. Try describing the "
            "product, material, or application in more detail."
        )
    }