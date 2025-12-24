from app import app, db
from models.user_model import ParkingLot, ParkingSpot

with app.app_context():

    # name, city, pin, max_spots, latitude, longitude
    parking_lots_data = [
        # DELHI
        ("Connaught Place Parking", "Delhi", "110001", 50, 28.6315, 77.2167),
        ("Karol Bagh Parking", "Delhi", "110005", 40, 28.6510, 77.1900),
        ("Saket Mall Parking", "Delhi", "110017", 35, 28.5246, 77.2066),
        ("Dwarka Sector 12 Parking", "Delhi", "110078", 45, 28.5963, 77.0426),
        ("Lajpat Nagar Parking", "Delhi", "110024", 30, 28.5690, 77.2432),

        # MUMBAI
        ("Bandra West Parking", "Mumbai", "400050", 60, 19.0596, 72.8295),
        ("Andheri East Parking", "Mumbai", "400069", 55, 19.1136, 72.8697),
        ("Colaba Causeway Parking", "Mumbai", "400001", 40, 18.9129, 72.8236),
        ("Powai Lake Parking", "Mumbai", "400076", 35, 19.1170, 72.9050),
        ("Malad West Parking", "Mumbai", "400064", 50, 19.1860, 72.8485),

        # BENGALURU
        ("MG Road Parking", "Bengaluru", "560001", 45, 12.9735, 77.6090),
        ("Koramangala Forum Mall Parking", "Bengaluru", "560095", 50, 12.9344, 77.6107),
        ("Whitefield ITPL Parking", "Bengaluru", "560066", 60, 12.9842, 77.7368),
        ("Electronic City Parking", "Bengaluru", "560100", 55, 12.8396, 77.6770),
        ("Yeshwanthpur Metro Parking", "Bengaluru", "560022", 40, 13.0174, 77.5560),

        # PUNE
        ("Shivajinagar Parking", "Pune", "411005", 35, 18.5309, 73.8478),
        ("Hinjewadi Phase 1 Parking", "Pune", "411057", 50, 18.5916, 73.7389),
        ("Viman Nagar Parking", "Pune", "411014", 40, 18.5679, 73.9143),
        ("Kothrud Parking", "Pune", "411038", 45, 18.5089, 73.8077),
        ("Koregaon Park Parking", "Pune", "411001", 30, 18.5362, 73.8938),

        # HYDERABAD
        ("Banjara Hills Parking", "Hyderabad", "500034", 40, 17.4156, 78.4346),
        ("Gachibowli Tech Park Parking", "Hyderabad", "500032", 60, 17.4410, 78.3498),
        ("Kukatpally Parking", "Hyderabad", "500072", 50, 17.4845, 78.4139),
        ("Secunderabad Station Parking", "Hyderabad", "500003", 55, 17.4399, 78.4983),
        ("Charminar Market Parking", "Hyderabad", "500002", 35, 17.3616, 78.4747),
    ]

    # Insert parking lots + create spots
    for name, city, pin, max_spots, lat, lng in parking_lots_data:
        lot = ParkingLot.query.filter_by(parking_name=name).first()

        if not lot:
            lot = ParkingLot(
                parking_name=name,
                price=20.0,
                address=f"{name}, {city}",
                pin_code=pin,
                max_spots=max_spots,
                latitude=lat,
                longitude=lng
            )
            db.session.add(lot)
            db.session.commit()
            print(f"🆕 Created lot: {lot.parking_name}")
        else:
            print(f"✔ Lot exists: {lot.parking_name}")

        # Create missing spots
        existing = ParkingSpot.query.filter_by(lot_id=lot.id).count()

        if existing < lot.max_spots:
            for i in range(existing + 1, lot.max_spots + 1):
                db.session.add(ParkingSpot(
                    lot_id=lot.id,
                    spot_number=str(i),
                    status='A'
                ))

            db.session.commit()

            print(f"➕ Added {lot.max_spots - existing} new spots to {lot.parking_name}")
        else:
            print(f"✔ {lot.parking_name} already has full {existing} spots")

    print("\n🎉 All parking lots + spots seeded with real coordinates!")
