from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
import re

from app.database import get_db
from app.models import Standard
from app.services.recommendation_service import recommend_standards
from app.routers.products import PRODUCTS
from app.routers.services import SERVICES


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
# PRODUCT REQUIREMENT DETECTION
# =========================================================

def detect_product_intent(query: str):
    """
    Detect whether the user is asking about
    product requirements.
    """

    text = query.lower().strip()

    requirement_words = [
        "requirement",
        "requirements",
        "require",
        "specification",
        "specifications",
        "what do i need",
        "what is needed",
        "applicable standard",
        "which standard",
        "standard for",
        "used for"
    ]

    has_requirement_intent = any(
        word in text
        for word in requirement_words
    )

    best_product = None
    best_score = 0

    for product in PRODUCTS:

        score = 0

        product_name = product["product"].lower()

        # Direct product name match
        if product_name in text:
            score += 20

        # Match individual words
        product_words = re.findall(
            r"[a-zA-Z0-9]+",
            product_name
        )

        for word in product_words:

            if len(word) > 2 and word in text:
                score += 5

        # Match requirements
        for requirement in product["requirements"]:

            requirement_words = re.findall(
                r"[a-zA-Z0-9]+",
                requirement.lower()
            )

            for word in requirement_words:

                if len(word) > 3 and word in text:
                    score += 2

        # Match category
        if product["category"].lower() in text:
            score += 5

        if score > best_score:
            best_score = score
            best_product = product

    if best_product and (
        has_requirement_intent or best_score >= 10
    ):
        return best_product

    return None


# =========================================================
# SERVICE INTENT DETECTION
# =========================================================

def detect_service_intent(query: str):
    """
    Detect BIS services such as:
    certification, ISI mark and licence.
    """

    text = query.lower().strip()

    best_service = None
    best_score = 0

    for service in SERVICES:

        score = 0

        name = service["name"].lower()
        description = service["description"].lower()

        # Service name match
        if name in text:
            score += 20

        # Description words
        description_words = re.findall(
            r"[a-zA-Z0-9]+",
            description
        )

        for word in description_words:

            if len(word) > 3 and word in text:
                score += 2

        # Keyword match
        for keyword in service["keywords"]:

            if keyword.lower() in text:
                score += 10

        if score > best_score:
            best_score = score
            best_service = service

    if best_service and best_score >= 8:
        return best_service

    return None


# =========================================================
# CREATE PRODUCT RESPONSE
# =========================================================

def create_product_response(
    db: Session,
    product: dict
):

    standard = find_standard_by_is_number(
        db,
        product["standard"]
    )

    source_url = None

    if standard:
        source_url = standard.source_url

    answer = (
        f"Product Requirements\n\n"
        f"{product['product']}\n\n"
        f"Applicable BIS Standard:\n"
        f"{product['standard']}\n\n"
        f"Requirements:\n"
    )

    for requirement in product["requirements"]:
        answer += f"• {requirement}\n"

    answer += (
        f"\nCategory:\n"
        f"{product['category']}"
    )

    return {
        "answer": answer,
        "product": {
            "id": product["id"],
            "product": product["product"],
            "category": product["category"],
            "standard": product["standard"],
            "requirements": product["requirements"],
            "source_url": source_url
        }
    }


# =========================================================
# CREATE SERVICE RESPONSE
# =========================================================

def create_service_response(service: dict):

    answer = (
        f"BIS Service\n\n"
        f"{service['name']}\n\n"
        f"{service['description']}\n\n"
        f"Category:\n"
        f"{service['category']}"
    )

    return {
        "answer": answer,
        "service": {
            "id": service["id"],
            "name": service["name"],
            "description": service["description"],
            "category": service["category"]
        }
    }


# =========================================================
# CREATE ASSISTANT-STYLE RECOMMENDATION ANSWER
# =========================================================

def create_recommendation_answer(
    best_match: dict,
    related_standards: list
):

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
    # 2. PRODUCT REQUIREMENTS
    # =====================================================

    product = detect_product_intent(query)

    if product:

        product_response = create_product_response(
            db,
            product
        )

        return {
            "query": query,
            "found": True,
            "response_type": "product_requirements",
            "answer": product_response["answer"],
            "product": product_response["product"]
        }


    # =====================================================
    # 3. BIS SERVICE
    # =====================================================

    service = detect_service_intent(query)

    if service:

        service_response = create_service_response(
            service
        )

        return {
            "query": query,
            "found": True,
            "response_type": "service_information",
            "answer": service_response["answer"],
            "service": service_response["service"]
        }


    # =====================================================
    # 4. EXPLICIT CATEGORY SEARCH
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
    # 5. NATURAL-LANGUAGE RECOMMENDATION
    # =====================================================

    all_standards = db.query(Standard).all()

    recommendations = recommend_standards(
        query,
        all_standards,
        limit=5
    )

    if recommendations:

        best_match = recommendations[0]

        related_standards = recommendations[1:]

        answer = create_recommendation_answer(
            best_match,
            related_standards
        )

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
                "reason": best_match["reason"],
                "source_url": best_match.get("source_url")
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
    # 6. NO MATCH
    # =====================================================

    return {
        "query": query,
        "found": False,
        "response_type": "no_match",
        "answer": (
            "I could not identify a matching BIS standard "
            "for your requirement. Try describing the "
            "product, material, service, or application "
            "in more detail."
        )
    }