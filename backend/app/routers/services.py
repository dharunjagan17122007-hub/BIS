from fastapi import APIRouter

router = APIRouter(
    prefix="/api/services",
    tags=["BIS Services"]
)


SERVICES = [
    {
        "id": 1,
        "name": "BIS Certification",
        "description": "Information about obtaining BIS certification for products.",
        "category": "Certification",
        "keywords": [
            "certification",
            "certificate",
            "bis certification",
            "certify"
        ]
    },
    {
        "id": 2,
        "name": "ISI Mark",
        "description": "Information about products covered under the ISI Mark certification scheme.",
        "category": "Marking",
        "keywords": [
            "isi mark",
            "isi",
            "mark",
            "product mark"
        ]
    },
    {
        "id": 3,
        "name": "BIS Licence",
        "description": "Information related to BIS licences and licensing requirements.",
        "category": "Licensing",
        "keywords": [
            "licence",
            "license",
            "bis licence",
            "bis license"
        ]
    },
    {
        "id": 4,
        "name": "Product Certification",
        "description": "Guidance for manufacturers seeking BIS product certification.",
        "category": "Certification",
        "keywords": [
            "product certification",
            "certify product",
            "product licence"
        ]
    },
    {
        "id": 5,
        "name": "BIS Standards Search",
        "description": "Search and identify relevant Indian Standards for products and requirements.",
        "category": "Standards",
        "keywords": [
            "standard search",
            "find standard",
            "search standard",
            "indian standard"
        ]
    }
]


@router.get("/")
def get_services():
    return {
        "found": True,
        "count": len(SERVICES),
        "services": SERVICES
    }


@router.get("/search")
def search_services(query: str):
    query = query.lower().strip()

    results = []

    for service in SERVICES:
        score = 0

        if query in service["name"].lower():
            score += 10

        if query in service["description"].lower():
            score += 5

        for keyword in service["keywords"]:
            if keyword in query:
                score += 8

        if score > 0:
            results.append({
                **service,
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
        "services": results[:5]
    }