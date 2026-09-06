from app.database import Base, engine, SessionLocal
from app.models import Standard


# Create database tables
Base.metadata.create_all(bind=engine)


# Open database session
db = SessionLocal()


standards = [
    Standard(
        is_number="IS 456",
        title="Plain and Reinforced Concrete",
        category="Construction",
        description="Code of practice for plain and reinforced concrete.",
        status="Active"
    ),
    Standard(
        is_number="IS 1786",
        title="High Strength Deformed Steel Bars and Wires",
        category="Construction",
        description="Requirements for high strength deformed steel bars and wires used for concrete reinforcement.",
        status="Active"
    ),
    Standard(
        is_number="IS 10500",
        title="Drinking Water",
        category="Water",
        description="Specification for drinking water quality.",
        status="Active"
    ),
]


# Add only standards that don't already exist
for standard in standards:
    existing = db.query(Standard).filter(
        Standard.is_number == standard.is_number
    ).first()

    if existing is None:
        db.add(standard)


db.commit()
db.close()

print("Database created and BIS standards added successfully.")