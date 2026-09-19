"""
Seeds the orders table with sample data so the order-lookup tool has
something real to query. Called automatically by database.init_db() the
first time the app runs (when the orders table is empty). Can also be run
directly: `python seed.py`.
"""

from sqlalchemy.orm import Session


def seed_orders(db: Session):
    from models import Order

    sample_orders = [
        Order(
            order_number="1001",
            customer_name="Ali Raza",
            item="TechNova Wireless Headphones",
            status="Delivered",
            tracking_number="TRK-88213",
            total_amount=4999.0,
            order_date="2026-09-02",
            expected_delivery="2026-09-06",
        ),
        Order(
            order_number="1002",
            customer_name="Sara Khan",
            item="TechNova Smartwatch Pro",
            status="Shipped",
            tracking_number="TRK-88214",
            total_amount=12999.0,
            order_date="2026-09-10",
            expected_delivery="2026-09-15",
        ),
        Order(
            order_number="1003",
            customer_name="Bilal Ahmed",
            item="TechNova UltraBook 14",
            status="Processing",
            tracking_number=None,
            total_amount=145999.0,
            order_date="2026-09-16",
            expected_delivery="2026-09-22",
        ),
        Order(
            order_number="1004",
            customer_name="Fatima Noor",
            item="TechNova USB-C Charger 65W",
            status="Cancelled",
            tracking_number=None,
            total_amount=1999.0,
            order_date="2026-09-05",
            expected_delivery=None,
        ),
        Order(
            order_number="1005",
            customer_name="Zohaib Iqbal",
            item="TechNova Mechanical Keyboard",
            status="Shipped",
            tracking_number="TRK-88220",
            total_amount=8499.0,
            order_date="2026-09-14",
            expected_delivery="2026-09-19",
        ),
        Order(
            order_number="1006",
            customer_name="Ayesha Malik",
            item="TechNova Bluetooth Speaker Mini",
            status="Delivered",
            tracking_number="TRK-88199",
            total_amount=3499.0,
            order_date="2026-08-28",
            expected_delivery="2026-09-01",
        ),
    ]

    db.add_all(sample_orders)
    db.commit()
    print(f"Seeded {len(sample_orders)} sample orders.")


if __name__ == "__main__":
    # Allow running as a standalone script: python seed.py
    from database import SessionLocal, init_db

    init_db()  # creates tables; seeds only if empty
    session = SessionLocal()
    from models import Order

    if session.query(Order).count() == 0:
        seed_orders(session)
    else:
        print("Orders table already has data; skipping seed.")
    session.close()
