"""
Seed Data Script for SevaConnect.

Run this to populate MongoDB with initial departments, services, and parts.
This saves you from manually entering data through the API.

Usage:
    cd backend
    python seed_data.py

Run this ONCE when setting up the project for the first time.
If you run it again, it will skip already-existing data.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from datetime import datetime
from common.db import db


def seed_departments():
    """Add the 5 main service departments."""
    departments = [
        {
            "name": "Vehicle Services",
            "description": "Bike and car repair, battery, tyre, and general vehicle maintenance",
            "icon": "🚗",
            "color": "#f97316",
            "order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Electrical Services",
            "description": "Switch, fan, wiring, MCB, and all home electrical work",
            "icon": "⚡",
            "color": "#eab308",
            "order": 2,
            "is_active": True,
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Home Services",
            "description": "Plumbing, carpentry, painting, and home cleaning",
            "icon": "🏠",
            "color": "#22c55e",
            "order": 3,
            "is_active": True,
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Appliance Services",
            "description": "AC, refrigerator, washing machine, geyser repair",
            "icon": "❄️",
            "color": "#3b82f6",
            "order": 4,
            "is_active": True,
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Computer & Electronics",
            "description": "Laptop, desktop, Wi-Fi router, and printer repair",
            "icon": "💻",
            "color": "#8b5cf6",
            "order": 5,
            "is_active": True,
            "created_at": datetime.utcnow(),
        },
    ]

    inserted = 0
    for dept in departments:
        # Skip if already exists
        existing = db.departments.find_one({"name": dept["name"]})
        if not existing:
            db.departments.insert_one(dept)
            inserted += 1
            print(f"  ✅ Added department: {dept['name']}")
        else:
            print(f"  ⏭️  Skipping (exists): {dept['name']}")

    return inserted


def seed_services():
    """Add services under each department."""
    # Get department IDs first
    dept_map = {}
    for dept in db.departments.find():
        dept_map[dept['name']] = dept['_id']

    if not dept_map:
        print("  ❌ No departments found. Run seed_departments first.")
        return 0

    services = [
        # Vehicle Services
        {
            "dept_name": "Vehicle Services",
            "name": "Bike Repair",
            "description": "General bike repair — engine, brakes, chain, lights",
            "icon": "🏍️",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 200,
            "labour_max": 800,
            "base_price": 350,
            "duration_minutes": 60,
        },
        {
            "dept_name": "Vehicle Services",
            "name": "Bike Starting Problem",
            "description": "Diagnose and fix bike starting issues — battery, self, spark plug",
            "icon": "🔋",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 150,
            "labour_max": 500,
            "base_price": 300,
            "duration_minutes": 45,
        },
        {
            "dept_name": "Vehicle Services",
            "name": "Car Repair",
            "description": "Car mechanical repairs — engine, brake, AC, electricals",
            "icon": "🚗",
            "visit_charge": 150,
            "inspection_charge": 100,
            "labour_min": 500,
            "labour_max": 3000,
            "base_price": 800,
            "duration_minutes": 120,
        },
        {
            "dept_name": "Vehicle Services",
            "name": "Battery Replacement",
            "description": "Vehicle battery testing and replacement",
            "icon": "🔋",
            "visit_charge": 100,
            "inspection_charge": 0,
            "labour_min": 100,
            "labour_max": 200,
            "base_price": 200,
            "duration_minutes": 30,
        },
        {
            "dept_name": "Vehicle Services",
            "name": "Tyre/Puncture",
            "description": "Puncture repair and tyre replacement",
            "icon": "🛞",
            "visit_charge": 100,
            "inspection_charge": 0,
            "labour_min": 50,
            "labour_max": 200,
            "base_price": 150,
            "duration_minutes": 30,
        },

        # Electrical Services
        {
            "dept_name": "Electrical Services",
            "name": "Fan Repair",
            "description": "Ceiling fan, table fan, and exhaust fan repair or replacement",
            "icon": "💨",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 100,
            "labour_max": 400,
            "base_price": 200,
            "duration_minutes": 45,
        },
        {
            "dept_name": "Electrical Services",
            "name": "Switch/Socket Repair",
            "description": "Repair or replace faulty switches, sockets, and plugs",
            "icon": "🔌",
            "visit_charge": 100,
            "inspection_charge": 0,
            "labour_min": 50,
            "labour_max": 200,
            "base_price": 150,
            "duration_minutes": 30,
        },
        {
            "dept_name": "Electrical Services",
            "name": "Light Installation",
            "description": "LED light, tube light, and bulb installation",
            "icon": "💡",
            "visit_charge": 100,
            "inspection_charge": 0,
            "labour_min": 50,
            "labour_max": 300,
            "base_price": 150,
            "duration_minutes": 30,
        },
        {
            "dept_name": "Electrical Services",
            "name": "Wiring Problem",
            "description": "Fix wiring faults, short circuits, and electrical issues",
            "icon": "⚡",
            "visit_charge": 100,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 1500,
            "base_price": 500,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Electrical Services",
            "name": "MCB/Power Problem",
            "description": "MCB tripping, power fluctuation, and distribution board issues",
            "icon": "🔧",
            "visit_charge": 100,
            "inspection_charge": 100,
            "labour_min": 200,
            "labour_max": 1000,
            "base_price": 400,
            "duration_minutes": 60,
        },

        # Home Services
        {
            "dept_name": "Home Services",
            "name": "Plumbing",
            "description": "Leakage, tap repair, pipe fitting, and drainage problems",
            "icon": "🚿",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 150,
            "labour_max": 800,
            "base_price": 300,
            "duration_minutes": 60,
        },
        {
            "dept_name": "Home Services",
            "name": "Carpenter",
            "description": "Door, window, furniture repair, and woodwork",
            "icon": "🪚",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 300,
            "labour_max": 1500,
            "base_price": 500,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Home Services",
            "name": "Home Cleaning",
            "description": "Deep cleaning, bathroom cleaning, kitchen cleaning",
            "icon": "🧹",
            "visit_charge": 0,
            "inspection_charge": 0,
            "labour_min": 500,
            "labour_max": 2000,
            "base_price": 800,
            "duration_minutes": 180,
        },

        # Appliance Services
        {
            "dept_name": "Appliance Services",
            "name": "AC Repair",
            "description": "AC not cooling, gas refill, compressor issues, cleaning",
            "icon": "❄️",
            "visit_charge": 150,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 2000,
            "base_price": 600,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Appliance Services",
            "name": "Refrigerator Repair",
            "description": "Fridge not cooling, compressor, thermostat, gas issues",
            "icon": "🧊",
            "visit_charge": 150,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 2500,
            "base_price": 600,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Appliance Services",
            "name": "Washing Machine Repair",
            "description": "Not spinning, not draining, leaking, control panel issues",
            "icon": "🫧",
            "visit_charge": 150,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 2000,
            "base_price": 600,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Appliance Services",
            "name": "Geyser Repair",
            "description": "Not heating, leaking, thermostat issues",
            "icon": "♨️",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 150,
            "labour_max": 800,
            "base_price": 300,
            "duration_minutes": 60,
        },

        # Computer & Electronics
        {
            "dept_name": "Computer & Electronics",
            "name": "Laptop Repair",
            "description": "Screen, keyboard, battery, charging port, software issues",
            "icon": "💻",
            "visit_charge": 100,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 2000,
            "base_price": 500,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Computer & Electronics",
            "name": "Desktop Repair",
            "description": "Not starting, slow, display issues, hardware upgrade",
            "icon": "🖥️",
            "visit_charge": 100,
            "inspection_charge": 100,
            "labour_min": 300,
            "labour_max": 2500,
            "base_price": 500,
            "duration_minutes": 90,
        },
        {
            "dept_name": "Computer & Electronics",
            "name": "Wi-Fi/Router Setup",
            "description": "Router configuration, Wi-Fi not working, speed issues",
            "icon": "📶",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 100,
            "labour_max": 400,
            "base_price": 200,
            "duration_minutes": 45,
        },
        {
            "dept_name": "Computer & Electronics",
            "name": "Printer Repair",
            "description": "Not printing, paper jam, cartridge issues, driver problems",
            "icon": "🖨️",
            "visit_charge": 100,
            "inspection_charge": 50,
            "labour_min": 150,
            "labour_max": 800,
            "base_price": 300,
            "duration_minutes": 60,
        },
    ]

    inserted = 0
    for svc in services:
        dept_id = dept_map.get(svc['dept_name'])
        if not dept_id:
            print(f"  ❌ Department not found: {svc['dept_name']}")
            continue

        existing = db.services.find_one({"name": svc['name'], "dept_id": dept_id})
        if not existing:
            service_doc = {
                "dept_id": dept_id,
                "name": svc['name'],
                "description": svc['description'],
                "icon": svc.get('icon', '🔧'),
                "visit_charge": svc.get('visit_charge', 100),
                "inspection_charge": svc.get('inspection_charge', 50),
                "labour_min": svc.get('labour_min', 0),
                "labour_max": svc.get('labour_max', 0),
                "base_price": svc.get('base_price', 0),
                "duration_minutes": svc.get('duration_minutes', 60),
                "is_active": True,
                "created_at": datetime.utcnow(),
            }
            db.services.insert_one(service_doc)
            inserted += 1
            print(f"  ✅ Added service: {svc['name']}")
        else:
            print(f"  ⏭️  Skipping (exists): {svc['name']}")

    return inserted


def seed_parts():
    """Add common spare parts used by technicians."""
    parts = [
        # Vehicle parts
        {"name": "Bike Battery (Lead Acid)", "category": "Vehicle", "min_price": 1200, "max_price": 2000, "unit": "piece", "stock": 20},
        {"name": "Bike Battery (Lithium)", "category": "Vehicle", "min_price": 3000, "max_price": 6000, "unit": "piece", "stock": 10},
        {"name": "Spark Plug", "category": "Vehicle", "min_price": 80, "max_price": 250, "unit": "piece", "stock": 50},
        {"name": "Starter Relay", "category": "Vehicle", "min_price": 200, "max_price": 500, "unit": "piece", "stock": 15},
        {"name": "Air Filter", "category": "Vehicle", "min_price": 100, "max_price": 400, "unit": "piece", "stock": 30},
        {"name": "Engine Oil (1 litre)", "category": "Vehicle", "min_price": 200, "max_price": 600, "unit": "litre", "stock": 50},
        {"name": "Brake Pad (Bike)", "category": "Vehicle", "min_price": 150, "max_price": 400, "unit": "pair", "stock": 25},
        {"name": "Chain Set", "category": "Vehicle", "min_price": 400, "max_price": 1000, "unit": "set", "stock": 15},
        {"name": "Car Battery", "category": "Vehicle", "min_price": 3500, "max_price": 8000, "unit": "piece", "stock": 10},

        # Electrical parts
        {"name": "MCB Switch (6A)", "category": "Electrical", "min_price": 150, "max_price": 300, "unit": "piece", "stock": 20},
        {"name": "MCB Switch (16A)", "category": "Electrical", "min_price": 200, "max_price": 400, "unit": "piece", "stock": 20},
        {"name": "Modular Switch", "category": "Electrical", "min_price": 50, "max_price": 200, "unit": "piece", "stock": 50},
        {"name": "Power Socket", "category": "Electrical", "min_price": 80, "max_price": 250, "unit": "piece", "stock": 40},
        {"name": "LED Bulb (9W)", "category": "Electrical", "min_price": 60, "max_price": 150, "unit": "piece", "stock": 100},
        {"name": "Tube Light (20W)", "category": "Electrical", "min_price": 150, "max_price": 350, "unit": "piece", "stock": 30},
        {"name": "Fan Capacitor", "category": "Electrical", "min_price": 80, "max_price": 200, "unit": "piece", "stock": 30},
        {"name": "Fan Regulator", "category": "Electrical", "min_price": 100, "max_price": 300, "unit": "piece", "stock": 20},
        {"name": "Electric Wire (per metre)", "category": "Electrical", "min_price": 15, "max_price": 40, "unit": "metre", "stock": 500},

        # Plumbing parts
        {"name": "Tap/Faucet", "category": "Plumbing", "min_price": 200, "max_price": 800, "unit": "piece", "stock": 15},
        {"name": "PVC Pipe (per foot)", "category": "Plumbing", "min_price": 30, "max_price": 80, "unit": "foot", "stock": 200},
        {"name": "Pipe Elbow/Coupling", "category": "Plumbing", "min_price": 20, "max_price": 60, "unit": "piece", "stock": 50},
        {"name": "Flush Tank Parts", "category": "Plumbing", "min_price": 150, "max_price": 500, "unit": "set", "stock": 10},

        # Appliance parts
        {"name": "AC Gas Refill (1 ton)", "category": "Appliance", "min_price": 800, "max_price": 1500, "unit": "service", "stock": 100},
        {"name": "AC Filter Cleaning", "category": "Appliance", "min_price": 200, "max_price": 400, "unit": "service", "stock": 100},
        {"name": "AC Capacitor", "category": "Appliance", "min_price": 300, "max_price": 800, "unit": "piece", "stock": 15},
        {"name": "Refrigerator Thermostat", "category": "Appliance", "min_price": 400, "max_price": 1000, "unit": "piece", "stock": 10},
        {"name": "Washing Machine Belt", "category": "Appliance", "min_price": 200, "max_price": 500, "unit": "piece", "stock": 15},
        {"name": "Geyser Heating Element", "category": "Appliance", "min_price": 300, "max_price": 800, "unit": "piece", "stock": 10},
        {"name": "Geyser Thermostat", "category": "Appliance", "min_price": 200, "max_price": 500, "unit": "piece", "stock": 10},

        # Computer parts
        {"name": "Laptop RAM (4GB)", "category": "Computer", "min_price": 800, "max_price": 1500, "unit": "piece", "stock": 10},
        {"name": "Laptop RAM (8GB)", "category": "Computer", "min_price": 1500, "max_price": 2500, "unit": "piece", "stock": 10},
        {"name": "Laptop Charger", "category": "Computer", "min_price": 500, "max_price": 1500, "unit": "piece", "stock": 15},
        {"name": "Laptop Battery", "category": "Computer", "min_price": 1500, "max_price": 4000, "unit": "piece", "stock": 8},
        {"name": "Thermal Paste", "category": "Computer", "min_price": 100, "max_price": 300, "unit": "piece", "stock": 30},
        {"name": "Hard Disk (500GB)", "category": "Computer", "min_price": 1500, "max_price": 3000, "unit": "piece", "stock": 8},
        {"name": "SSD (256GB)", "category": "Computer", "min_price": 2000, "max_price": 4000, "unit": "piece", "stock": 8},
    ]

    inserted = 0
    for part in parts:
        existing = db.parts.find_one({"name": part['name']})
        if not existing:
            part_doc = {
                **part,
                "description": "",
                "is_active": True,
                "created_at": datetime.utcnow(),
            }
            db.parts.insert_one(part_doc)
            inserted += 1
            print(f"  ✅ Added part: {part['name']}")
        else:
            print(f"  ⏭️  Skipping (exists): {part['name']}")

    return inserted


if __name__ == "__main__":
    print("\n🌱 SevaConnect Seed Data Script")
    print("=" * 40)

    print("\n📁 Seeding Departments...")
    d = seed_departments()

    print("\n⚙️  Seeding Services...")
    s = seed_services()

    print("\n🔧 Seeding Parts...")
    p = seed_parts()

    print(f"\n✅ Done!")
    print(f"   Departments added: {d}")
    print(f"   Services added: {s}")
    print(f"   Parts added: {p}")
    print("\nYour SevaConnect database is ready. Start the server with:")
    print("   python manage.py runserver\n")
