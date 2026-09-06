import re
from typing import List

from app.models import Standard


STOP_WORDS = {
    "a", "an", "the", "for", "of", "to", "and", "or",
    "is", "are", "was", "were", "what", "which", "standard",
    "standards", "specification", "specifications", "code",
    "practice", "used", "use", "need", "needed", "required",
    "requirements", "requirement", "cover", "covers", "covering",
    "tell", "me", "please", "i", "want", "looking",
    "manufacture", "manufacturing", "make", "makes", "produce",
    "producing", "product", "products", "apply", "applies",
    "applicable"
}


KEYWORD_SYNONYMS = {
    "bars": [
        "bar",
        "bars",
        "reinforcement",
        "steel"
    ],

    "bar": [
        "bar",
        "bars",
        "reinforcement",
        "steel"
    ],

    "reinforcement": [
        "reinforcement",
        "reinforced",
        "concrete",
        "steel"
    ],

    "cement": [
        "cement",
        "portland",
        "concrete"
    ],

    "water": [
        "water",
        "drinking",
        "potable",
        "quality"
    ],

    "cable": [
        "cable",
        "electric",
        "electrical",
        "wire"
    ],

    "pipes": [
        "pipe",
        "pipes",
        "concrete"
    ],

    "pipe": [
        "pipe",
        "pipes",
        "concrete"
    ],

    "steel": [
        "steel",
        "bars",
        "reinforcement",
        "construction"
    ],

    "food": [
        "food",
        "agriculture"
    ]
}


def extract_keywords(text: str) -> List[str]:
    """
    Extract useful keywords from the user's query.
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    ]


def expand_keywords(keywords: List[str]) -> List[str]:
    """
    Expand user keywords using predefined synonyms.
    """

    expanded = set(keywords)

    for keyword in keywords:

        synonyms = KEYWORD_SYNONYMS.get(
            keyword,
            []
        )

        for synonym in synonyms:
            expanded.add(synonym)

    return list(expanded)


def calculate_score(
    standard: Standard,
    keywords: List[str]
) -> int:
    """
    Calculate relevance score for a BIS standard.

    IS number  -> +10
    Title      -> +8
    Category   -> +5
    Description -> +3
    """

    score = 0

    is_number = (
        standard.is_number or ""
    ).lower()

    title = (
        standard.title or ""
    ).lower()

    category = (
        standard.category or ""
    ).lower()

    description = (
        standard.description or ""
    ).lower()

    for keyword in keywords:

        if keyword in is_number:
            score += 10

        if keyword in title:
            score += 8

        if keyword in category:
            score += 5

        if keyword in description:
            score += 3

    return score


def recommend_standards(
    query: str,
    standards: List[Standard],
    limit: int = 5
) -> List[dict]:
    """
    Find the most relevant BIS standards
    for a natural-language requirement.
    """

    # Step 1: Extract keywords
    keywords = extract_keywords(query)

    if not keywords:
        return []

    # Step 2: Expand keywords
    expanded_keywords = expand_keywords(
        keywords
    )

    recommendations = []

    # Step 3: Calculate score for every standard
    for standard in standards:

        score = calculate_score(
            standard,
            expanded_keywords
        )

        # Ignore standards with no match
        if score <= 0:
            continue

        # Initially every result is Related.
        # The best result will become Primary later.
        match_type = "Related"

        # Find keywords actually appearing
        # in title or description
        matched_keywords = [
            keyword
            for keyword in expanded_keywords
            if keyword in (
                standard.title or ""
            ).lower()
            or keyword in (
                standard.description or ""
            ).lower()
        ]

        # Remove duplicate keywords
        matched_keywords = list(
            dict.fromkeys(matched_keywords)
        )

        # Generate human-readable explanation
        if matched_keywords:

            reason = (
                f"{standard.is_number} is recommended because it "
                f"specifically covers {standard.title.lower()}."
            )

        else:

            reason = (
                f"{standard.is_number} is related to your "
                f"requested requirement."
            )

        # Add recommendation
        recommendations.append({
            "is_number": standard.is_number,
            "title": standard.title,
            "category": standard.category,
            "description": standard.description,
            "status": standard.status,
            "source_url": standard.source_url,
            "relevance_score": score,
            "match_type": match_type,
            "reason": reason
        })

    # Step 4: Sort by relevance score
    recommendations.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    # Step 5: Mark the highest-scoring result
    # as the Primary recommendation
    if recommendations:

        recommendations[0]["match_type"] = "Primary"

    # Step 6: Return only the requested number
    return recommendations[:limit]