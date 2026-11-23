
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash


# Always use the database file in the project folder.
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "lablink.db"


DEPARTMENTS = [
    "Computer Science and Engineering",
    "Artificial Intelligence and Machine Learning",
    "Information Science and Engineering",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Biotechnology",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Data Science",
    "Cyber Security"
]


def get_db():
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Each department has six equipment types.
# Tuple format:
# name, category, description, quantity, location

EQUIPMENT_DATA = [
    # COMPUTER SCIENCE AND ENGINEERING
    ("GPU Workstation", "Computing", "High-performance workstation for programming and development.", 5, "CSE Lab"),
    ("Raspberry Pi Kit", "Development Kit", "Single-board computer for software and hardware projects.", 8, "CSE Lab"),
    ("Arduino Uno", "Development Kit", "Microcontroller board for embedded projects.", 10, "CSE Lab"),
    ("3D Printer", "Fabrication", "Printer for creating project prototypes.", 2, "Innovation Lab"),
    ("VR Development Kit", "Development Kit", "Virtual reality development equipment.", 4, "CSE Lab"),
    ("High Performance Desktop", "Computing", "Desktop system for software development.", 8, "CSE Lab"),

    # ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING
    ("AI GPU Workstation", "Computing", "GPU workstation for AI model development.", 5, "AI Lab"),
    ("NVIDIA Jetson Nano", "Development Kit", "AI edge computing development board.", 8, "AI Lab"),
    ("Deep Learning Workstation", "Computing", "Workstation for deep learning experiments.", 4, "AI Lab"),
    ("AI Vision Camera", "Camera", "Camera for computer vision experiments.", 6, "AI Lab"),
    ("Edge AI Kit", "Development Kit", "Hardware kit for edge AI applications.", 8, "AI Lab"),
    ("Tensor Processing Unit", "Computing", "Accelerator for machine learning workloads.", 3, "AI Lab"),

    # INFORMATION SCIENCE AND ENGINEERING
    ("Database Server", "Computing", "Server for database development and testing.", 4, "ISE Lab"),
    ("Networking Switch", "Networking", "Managed network switch for networking practice.", 6, "ISE Lab"),
    ("Raspberry Pi", "Development Kit", "Board for application and IoT development.", 8, "ISE Lab"),
    ("Cloud Computing Workstation", "Computing", "System for cloud computing experiments.", 5, "ISE Lab"),
    ("Web Development Workstation", "Computing", "Desktop for web application development.", 8, "ISE Lab"),
    ("Network Testing Kit", "Networking", "Equipment for network testing and learning.", 5, "ISE Lab"),

    # ELECTRONICS AND COMMUNICATION ENGINEERING
    ("Digital Oscilloscope", "Testing", "Instrument for viewing electronic signals.", 6, "ECE Lab"),
    ("Function Generator", "Testing", "Generates electrical waveforms for experiments.", 6, "ECE Lab"),
    ("Arduino Sensor Kit", "Development Kit", "Sensor kit for electronics projects.", 10, "ECE Lab"),
    ("Communication Trainer Kit", "Training Kit", "Kit for communication system experiments.", 5, "ECE Lab"),
    ("Spectrum Analyzer", "Testing", "Instrument for signal frequency analysis.", 3, "ECE Lab"),
    ("IoT Development Kit", "Development Kit", "Hardware kit for IoT applications.", 8, "ECE Lab"),

    # ELECTRICAL AND ELECTRONICS ENGINEERING
    ("Digital Multimeter", "Testing", "Instrument for electrical measurements.", 10, "EEE Lab"),
    ("Power Supply Unit", "Testing", "Regulated power supply for experiments.", 8, "EEE Lab"),
    ("Transformer Trainer Kit", "Training Kit", "Equipment for transformer experiments.", 5, "EEE Lab"),
    ("Motor Control Kit", "Development Kit", "Kit for motor control experiments.", 6, "EEE Lab"),
    ("Solar Panel Trainer", "Renewable Energy", "Solar energy experiment kit.", 4, "EEE Lab"),
    ("Digital Power Analyzer", "Testing", "Instrument for electrical power analysis.", 3, "EEE Lab"),

    # MECHANICAL ENGINEERING
    ("3D Printer", "Fabrication", "Equipment for creating 3D prototypes.", 3, "Mechanical Lab"),
    ("CNC Machine", "Manufacturing", "Computer-controlled machining equipment.", 2, "Mechanical Lab"),
    ("Lathe Machine", "Manufacturing", "Machine for turning and shaping materials.", 3, "Mechanical Lab"),
    ("Drilling Machine", "Manufacturing", "Equipment for drilling operations.", 4, "Mechanical Lab"),
    ("Universal Testing Machine", "Testing", "Machine for material strength testing.", 2, "Mechanical Lab"),
    ("Laser Cutting Machine", "Fabrication", "Equipment for precision cutting.", 2, "Mechanical Lab"),

    # CIVIL ENGINEERING
    ("Concrete Testing Machine", "Testing", "Machine for testing concrete strength.", 3, "Civil Lab"),
    ("Soil Testing Kit", "Testing", "Kit for soil analysis experiments.", 6, "Civil Lab"),
    ("Total Station", "Surveying", "Instrument for land surveying.", 4, "Civil Lab"),
    ("Digital Theodolite", "Surveying", "Instrument for measuring horizontal and vertical angles.", 5, "Civil Lab"),
    ("Compression Testing Machine", "Testing", "Machine for compression strength tests.", 2, "Civil Lab"),
    ("Laser Distance Meter", "Surveying", "Device for accurate distance measurement.", 6, "Civil Lab"),

    # BIOTECHNOLOGY
    ("Compound Microscope", "Laboratory", "Microscope for observing biological samples.", 8, "Biotechnology Lab"),
    ("Centrifuge Machine", "Laboratory", "Equipment for separating sample components.", 4, "Biotechnology Lab"),
    ("PCR Machine", "Laboratory", "Equipment for DNA amplification experiments.", 3, "Biotechnology Lab"),
    ("Digital Spectrophotometer", "Testing", "Instrument for measuring light absorbance.", 4, "Biotechnology Lab"),
    ("Electrophoresis Unit", "Laboratory", "Equipment for biomolecule separation experiments.", 5, "Biotechnology Lab"),
    ("Incubator", "Laboratory", "Equipment for controlled-temperature incubation.", 4, "Biotechnology Lab"),

    # CHEMICAL ENGINEERING
    ("pH Meter", "Testing", "Instrument for measuring solution pH.", 8, "Chemical Lab"),
    ("Digital Weighing Balance", "Testing", "Precision balance for laboratory measurements.", 8, "Chemical Lab"),
    ("Hot Plate Stirrer", "Laboratory", "Equipment for heating and mixing solutions.", 6, "Chemical Lab"),
    ("Distillation Unit", "Laboratory", "Equipment for separation experiments.", 3, "Chemical Lab"),
    ("Viscometer", "Testing", "Instrument for measuring fluid viscosity.", 4, "Chemical Lab"),
    ("Conductivity Meter", "Testing", "Instrument for measuring electrical conductivity.", 5, "Chemical Lab"),

    # AEROSPACE ENGINEERING
    ("Wind Tunnel", "Testing", "Equipment for airflow and aerodynamic experiments.", 2, "Aerospace Lab"),
    ("Drone Development Kit", "Development Kit", "Kit for drone design and development.", 5, "Aerospace Lab"),
    ("Flight Simulator", "Simulation", "System for flight simulation experiments.", 3, "Aerospace Lab"),
    ("Propeller Testing Kit", "Testing", "Equipment for propeller performance experiments.", 4, "Aerospace Lab"),
    ("Rocket Model Kit", "Development Kit", "Kit for educational aerospace projects.", 6, "Aerospace Lab"),
    ("Aerodynamics Workstation", "Computing", "Workstation for aerodynamic simulations.", 4, "Aerospace Lab"),

    # DATA SCIENCE
    ("Data Analytics Workstation", "Computing", "Workstation for data analysis projects.", 8, "Data Science Lab"),
    ("GPU Computing Server", "Computing", "Server for large-scale data processing.", 3, "Data Science Lab"),
    ("Data Visualization System", "Computing", "System for interactive data visualization.", 5, "Data Science Lab"),
    ("Big Data Processing Server", "Computing", "Server for big data experiments.", 3, "Data Science Lab"),
    ("Raspberry Pi Cluster", "Development Kit", "Cluster for distributed computing experiments.", 4, "Data Science Lab"),
    ("High Memory Workstation", "Computing", "Workstation for memory-intensive data analysis.", 6, "Data Science Lab"),

    # CYBER SECURITY
    ("Network Security Workstation", "Computing", "Workstation for network security learning.", 6, "Cyber Security Lab"),
    ("Firewall Testing Appliance", "Networking", "Appliance for firewall configuration practice.", 3, "Cyber Security Lab"),
    ("Network Analyzer", "Networking", "Tool for network traffic analysis.", 5, "Cyber Security Lab"),
    ("Raspberry Pi Security Kit", "Development Kit", "Board for security education projects.", 6, "Cyber Security Lab"),
    ("Server Testing Machine", "Computing", "Server for authorized security testing in a lab.", 4, "Cyber Security Lab"),
    ("Hardware Security Module", "Security", "Device for learning hardware-based security concepts.", 2, "Cyber Security Lab")
]


def add_missing_column(cursor, table_name, column_name, column_definition):
    """Add a column only if it does not already exist."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row["name"] for row in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    try:
        # USERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                usn TEXT,
                academic_year TEXT,
                semester TEXT,
                faculty_id TEXT,
                designation TEXT
            )
        """)

        # EQUIPMENT TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                department TEXT NOT NULL,
                description TEXT,
                quantity INTEGER DEFAULT 1,
                location TEXT,
                status TEXT DEFAULT 'Available'
            )
        """)

        # BOOKINGS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                equipment_id INTEGER,
                project_name TEXT,
                purpose TEXT,
                requirements TEXT,
                booking_date TEXT,
                start_time TEXT,
                end_time TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'Pending',
                faculty_note TEXT,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(equipment_id) REFERENCES equipment(id)
            )
        """)

        # Safely add columns if an older version of the database is used.
        add_missing_column(cursor, "users", "department", "TEXT")
        add_missing_column(cursor, "users", "usn", "TEXT")
        add_missing_column(cursor, "users", "academic_year", "TEXT")
        add_missing_column(cursor, "users", "semester", "TEXT")
        add_missing_column(cursor, "users", "faculty_id", "TEXT")
        add_missing_column(cursor, "users", "designation", "TEXT")

        add_missing_column(cursor, "equipment", "category", "TEXT")
        add_missing_column(cursor, "equipment", "department", "TEXT")
        add_missing_column(cursor, "equipment", "description", "TEXT")
        add_missing_column(cursor, "equipment", "quantity", "INTEGER DEFAULT 1")
        add_missing_column(cursor, "equipment", "location", "TEXT")
        add_missing_column(cursor, "equipment", "status", "TEXT DEFAULT 'Available'")

        add_missing_column(cursor, "bookings", "project_name", "TEXT")
        add_missing_column(cursor, "bookings", "purpose", "TEXT")
        add_missing_column(cursor, "bookings", "requirements", "TEXT")
        add_missing_column(cursor, "bookings", "booking_date", "TEXT")
        add_missing_column(cursor, "bookings", "start_time", "TEXT")
        add_missing_column(cursor, "bookings", "end_time", "TEXT")
        add_missing_column(cursor, "bookings", "deadline", "TEXT")
        add_missing_column(cursor, "bookings", "status", "TEXT DEFAULT 'Pending'")
        add_missing_column(cursor, "bookings", "faculty_note", "TEXT")

        # Insert missing equipment without deleting existing equipment.
        for index, item in enumerate(EQUIPMENT_DATA):
            name, category, description, quantity, location = item

            department_index = index // 6
            department = DEPARTMENTS[department_index]

            cursor.execute("""
                SELECT id
                FROM equipment
                WHERE name = ? AND department = ?
            """, (name, department))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO equipment (
                        name,
                        category,
                        department,
                        description,
                        quantity,
                        location,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    category,
                    department,
                    description,
                    quantity,
                    location,
                    "Available"
                ))

        # Create demo student only if the email does not exist.
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            ("student@lablink.com",)
        )

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO users (
                    name, email, password, role, department,
                    usn, academic_year, semester
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Demo Student",
                "student@lablink.com",
                generate_password_hash("student123"),
                "student",
                DEPARTMENTS[0],
                "1RU23CS001",
                "3rd Year",
                "5th Semester"
            ))

        # Create demo faculty only if the email does not exist.
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            ("faculty@lablink.com",)
        )

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO users (
                    name, email, password, role, department,
                    faculty_id, designation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Demo Faculty",
                "faculty@lablink.com",
                generate_password_hash("faculty123"),
                "faculty",
                DEPARTMENTS[0],
                "FAC001",
                "Assistant Professor"
            ))

        # Helpful indexes for booking lookups.
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_equipment_date
            ON bookings(equipment_id, booking_date, status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_student
            ON bookings(student_id)
        """)

        conn.commit()

        print("LabLink database initialized successfully!")
        print("12 departments configured.")
        print("72 equipment types configured (6 per department).")
        print("Existing users and bookings have been preserved.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
