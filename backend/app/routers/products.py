from fastapi import APIRouter

router = APIRouter(
    prefix="/api/products",
    tags=["BIS Product Requirements"]
)


PRODUCTS = [
    {
        "id": 1,
        "product": "Steel Reinforcement Bars",
        "category": "Construction",
        "standard": "IS 1786",
        "requirements": [
            "High strength deformed steel bars",
            "Concrete reinforcement",
            "Product conformity to applicable requirements"
        ]
    },
    {
        "id": 2,
        "product": "Plain and Reinforced Concrete",
        "category": "Construction",
        "standard": "IS 456",
        "requirements": [
            "Plain concrete",
            "Reinforced concrete",
            "Structural concrete design and construction"
        ]
    },
    {
        "id": 3,
        "product": "Drinking Water",
        "category": "Water & Environment",
        "standard": "IS 10500",
        "requirements": [
            "Drinking water quality",
            "Physical requirements",
            "Chemical requirements",
            "Microbiological requirements"
        ]
    },
    {
        "id": 4,
        "product": "Cement",
        "category": "Construction",
        "standard": "IS 269",
        "requirements": [
            "Ordinary Portland Cement",
            "Cement quality requirements",
            "Applicable testing requirements"
        ]
    },
    {
        "id": 5,
        "product": "Electrical Cables",
        "category": "Electrical",
        "standard": "IS 694",
        "requirements": [
            "Electric cables",
            "PVC insulated cables",
            "Electrical safety requirements"
        ]
    }
]


@router.get("/")
def get_products():
    return {
        "found": True,
        "count": len(PRODUCTS),
        "products": PRODUCTS
    }


@router.get("/search")
def search_products(query: str):
    query = query.lower().strip()

    results = []

    for product in PRODUCTS:
        score = 0

        product_name = product["product"].lower()

        if query in product_name:
            score += 10

        if query in product["category"].lower():
            score += 5

        for requirement in product["requirements"]:
            if query in requirement.lower():
                score += 5

        if score > 0:
            results.append({
                **product,
                "relevance_score": score
            })

    results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    return {
        "query": query,
        "found": len(results) > 0,
        "count": len(results),
        "products": results[:5]
    }