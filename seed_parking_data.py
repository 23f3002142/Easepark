from app import app, db
from models.user_model import ParkingLot, ParkingSpot

with app.app_context():
    # ✅ Exact parking names from your seeded data
    target_lots = [
        # Delhi
        "Connaught Place Parking",
        "Karol Bagh Parking",
        "Saket Mall Parking",
        "Dwarka Sector 12 Parking",
        "Lajpat Nagar Parking",
        # Mumbai
        "Bandra West Parking",
        "Andheri East Parking",
        "Colaba Causeway Parking",
        "Powai Lake Parking",
        "Malad West Parking",
        # Bengaluru
        "MG Road Parking",
        "Koramangala Forum Mall Parking",
        "Whitefield ITPL Parking",
        "Electronic City Parking",
        "Yeshwanthpur Metro Parking",
        # Pune
        "Shivajinagar Parking",
        "Hinjewadi Phase 1 Parking",
        "Viman Nagar Parking",
        "Kothrud Parking",
        "Koregaon Park Parking",
        # Hyderabad
        "Banjara Hills Parking",
        "Gachibowli Tech Park Parking",
        "Kukatpally Parking",
        "Secunderabad Station Parking",
        "Charminar Market Parking",
    ]

    for name in target_lots:
        lot = ParkingLot.query.filter_by(parking_name=name).first()

        if not lot:
            print(f"⚠️ Lot '{name}' not found in DB, skipping...")
            continue

        existing_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        if existing_spots >= lot.max_spots:
            print(f"✅ '{name}' already has {existing_spots} spots, skipping.")
            continue

        # Create remaining spots
        for i in range(existing_spots + 1, lot.max_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=str(i),
                status='A'
            )
            db.session.add(spot)

        db.session.commit()
        added = lot.max_spots - existing_spots
        print(f"✅ Added {added} spots for '{name}'")

    print("🎯 Spot creation completed successfully!")
