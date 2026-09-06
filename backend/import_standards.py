import csv

from app.database import SessionLocal
from app.models import Standard


def import_standards():
    db = SessionLocal()

    try:
        with open("data/standards.csv", "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                is_number = row["is_number"].strip()

                standard = (
                    db.query(Standard)
                    .filter(Standard.is_number == is_number)
                    .first()
                )

                if standard:
                    standard.title = row["title"].strip()
                    standard.category = row["category"].strip()
                    standard.description = row["description"].strip()
                    standard.status = row["status"].strip()
                    standard.source_url = row["source_url"].strip()

                else:
                    new_standard = Standard(
                        is_number=is_number,
                        title=row["title"].strip(),
                        category=row["category"].strip(),
                        description=row["description"].strip(),
                        status=row["status"].strip(),
                        source_url=row["source_url"].strip(),
                    )

                    db.add(new_standard)

            db.commit()
            print("Standards imported successfully.")

    except Exception as e:
        db.rollback()
        print(f"Import failed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    import_standards()