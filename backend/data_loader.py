"""
Sample Data Loader for GraphGuard AI.

Creates a realistic fraud scenario with:
- 20 users (5 in a fraud ring, 15 legitimate)
- Shared devices and phones among fraud ring members
- Circular money transfers
- Normal transaction patterns for legitimate users
"""

import pyTigerGraph as tg
import os
import time


TG_HOST = os.getenv("TG_HOST", "http://localhost")
TG_REST_PORT = os.getenv("TG_REST_PORT", "9000")
TG_GS_PORT = os.getenv("TG_GS_PORT", "14240")
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")


def load_sample_data():
    """Load sample fraud detection data into TigerGraph."""

    # Connect to TigerGraph
    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
        graphname="FraudGraph",
    )
    try:
        conn.getToken(conn.createSecret())
    except Exception:
        pass

    print("[DataLoader] Connected to TigerGraph. Loading sample data...")

    # ========================================
    # USERS - 5 fraudsters + 15 legitimate
    # ========================================
    fraud_users = [
        ("F001", "Viktor Petrov", "vpetrov@darkmail.com", "2024-01-15", True),
        ("F002", "Elena Kozlov", "ekozlov@tempmail.net", "2024-01-16", True),
        ("F003", "Dmitri Volkov", "dvolkov@fakebox.io", "2024-01-17", True),
        ("F004", "Anya Sokolov", "asokolov@burner.org", "2024-01-18", True),
        ("F005", "Boris Ivanov", "bivanov@shadow.cc", "2024-01-19", True),
    ]

    legit_users = [
        ("L001", "Sarah Johnson", "sarah.j@gmail.com", "2023-06-01", False),
        ("L002", "Michael Chen", "m.chen@outlook.com", "2023-07-15", False),
        ("L003", "Emily Davis", "emily.d@yahoo.com", "2023-08-20", False),
        ("L004", "James Wilson", "j.wilson@gmail.com", "2023-09-10", False),
        ("L005", "Priya Patel", "priya.p@gmail.com", "2023-10-05", False),
        ("L006", "David Kim", "d.kim@outlook.com", "2023-11-12", False),
        ("L007", "Maria Garcia", "m.garcia@gmail.com", "2023-12-01", False),
        ("L008", "Ahmed Hassan", "a.hassan@yahoo.com", "2024-01-08", False),
        ("L009", "Lisa Wang", "l.wang@gmail.com", "2024-02-14", False),
        ("L010", "Robert Brown", "r.brown@outlook.com", "2024-03-01", False),
        ("L011", "Nina Patel", "n.patel@gmail.com", "2023-05-22", False),
        ("L012", "Tom Anderson", "t.anderson@yahoo.com", "2023-06-30", False),
        ("L013", "Olivia Martinez", "o.martinez@gmail.com", "2023-08-11", False),
        ("L014", "Kevin Lee", "k.lee@outlook.com", "2023-09-25", False),
        ("L015", "Hannah Smith", "h.smith@gmail.com", "2023-11-03", False),
    ]

    all_users = fraud_users + legit_users

    # ========================================
    # PHONES
    # ========================================
    phones = [
        # Fraud ring phones - SHARED between multiple users
        ("+1-555-0101", "BurnerNet"),   # Shared by F001, F002, F003
        ("+1-555-0102", "BurnerNet"),   # Shared by F003, F004
        ("+1-555-0103", "ShadowMobile"),  # F005
        # Legitimate phones - one per user
        ("+1-555-1001", "Verizon"),
        ("+1-555-1002", "AT&T"),
        ("+1-555-1003", "T-Mobile"),
        ("+1-555-1004", "Verizon"),
        ("+1-555-1005", "AT&T"),
        ("+1-555-1006", "T-Mobile"),
        ("+1-555-1007", "Verizon"),
        ("+1-555-1008", "AT&T"),
        ("+1-555-1009", "T-Mobile"),
        ("+1-555-1010", "Verizon"),
        ("+1-555-1011", "AT&T"),
        ("+1-555-1012", "T-Mobile"),
        ("+1-555-1013", "Verizon"),
        ("+1-555-1014", "AT&T"),
        ("+1-555-1015", "T-Mobile"),
    ]

    # ========================================
    # DEVICES
    # ========================================
    devices = [
        # Fraud ring devices - SHARED
        ("DEV-X001", "Android", "Android 12"),  # Shared by F001, F002, F004
        ("DEV-X002", "Laptop", "Windows 11"),   # Shared by F003, F005
        # Legit devices
        ("DEV-L001", "iPhone", "iOS 17"),
        ("DEV-L002", "Android", "Android 14"),
        ("DEV-L003", "iPhone", "iOS 16"),
        ("DEV-L004", "Android", "Android 13"),
        ("DEV-L005", "iPhone", "iOS 17"),
        ("DEV-L006", "Android", "Android 14"),
        ("DEV-L007", "iPad", "iPadOS 17"),
        ("DEV-L008", "Android", "Android 13"),
        ("DEV-L009", "iPhone", "iOS 17"),
        ("DEV-L010", "Laptop", "macOS 14"),
        ("DEV-L011", "iPhone", "iOS 16"),
        ("DEV-L012", "Android", "Android 14"),
        ("DEV-L013", "iPhone", "iOS 17"),
        ("DEV-L014", "Android", "Android 13"),
        ("DEV-L015", "Laptop", "Windows 11"),
    ]

    # ========================================
    # BANK ACCOUNTS
    # ========================================
    accounts = [
        # Fraud ring accounts
        ("ACC-F001", "ShadowBank", 15200.0),
        ("ACC-F002", "ShadowBank", 8900.0),
        ("ACC-F003", "CryptoPay", 22000.0),
        ("ACC-F004", "ShadowBank", 5600.0),
        ("ACC-F005", "CryptoPay", 31000.0),
        # Legit accounts
        ("ACC-L001", "Chase", 45000.0),
        ("ACC-L002", "BankOfAmerica", 32000.0),
        ("ACC-L003", "Wells Fargo", 28000.0),
        ("ACC-L004", "Chase", 55000.0),
        ("ACC-L005", "HDFC Bank", 41000.0),
        ("ACC-L006", "Citi Bank", 19000.0),
        ("ACC-L007", "Chase", 67000.0),
        ("ACC-L008", "BankOfAmerica", 23000.0),
        ("ACC-L009", "Wells Fargo", 38000.0),
        ("ACC-L010", "Chase", 52000.0),
        ("ACC-L011", "HDFC Bank", 29000.0),
        ("ACC-L012", "Citi Bank", 44000.0),
        ("ACC-L013", "Chase", 36000.0),
        ("ACC-L014", "BankOfAmerica", 27000.0),
        ("ACC-L015", "Wells Fargo", 48000.0),
    ]

    # ========================================
    # UPSERT VERTICES
    # ========================================
    print("[DataLoader] Upserting vertices...")

    for uid, name, email, created, flagged in all_users:
        conn.upsertVertex("User", uid, {
            "name": name,
            "email": email,
            "created_at": created,
            "is_flagged": flagged,
        })

    for number, carrier in phones:
        conn.upsertVertex("Phone", number, {"carrier": carrier})

    for dev_id, dev_type, dev_os in devices:
        conn.upsertVertex("Device", dev_id, {"device_type": dev_type, "os": dev_os})

    for acc_num, bank, balance in accounts:
        conn.upsertVertex("BankAccount", acc_num, {"bank_name": bank, "balance": balance})

    # ========================================
    # UPSERT EDGES
    # ========================================
    print("[DataLoader] Upserting edges...")

    # --- HAS_PHONE edges ---
    # Fraud ring phone sharing
    phone_map = {
        "F001": ["+1-555-0101"],
        "F002": ["+1-555-0101"],
        "F003": ["+1-555-0101", "+1-555-0102"],
        "F004": ["+1-555-0102"],
        "F005": ["+1-555-0103"],
    }
    for uid, phone_list in phone_map.items():
        for phone in phone_list:
            conn.upsertEdge("User", uid, "HAS_PHONE", "Phone", phone, {"since": "2024-01"})

    # Legit users: one phone each
    for i in range(15):
        uid = f"L{str(i+1).zfill(3)}"
        phone = phones[3 + i][0]
        conn.upsertEdge("User", uid, "HAS_PHONE", "Phone", phone, {"since": "2023-06"})

    # --- USES_DEVICE edges ---
    # Fraud ring device sharing
    device_map = {
        "F001": ["DEV-X001"],
        "F002": ["DEV-X001"],
        "F003": ["DEV-X002"],
        "F004": ["DEV-X001"],
        "F005": ["DEV-X002"],
    }
    for uid, dev_list in device_map.items():
        for dev in dev_list:
            conn.upsertEdge("User", uid, "USES_DEVICE", "Device", dev, {"last_used": "2024-03"})

    # Legit users: one device each
    for i in range(15):
        uid = f"L{str(i+1).zfill(3)}"
        dev = devices[2 + i][0]
        conn.upsertEdge("User", uid, "USES_DEVICE", "Device", dev, {"last_used": "2024-03"})

    # --- OWNS_ACCOUNT edges ---
    for i, (uid, *_) in enumerate(all_users):
        acc = accounts[i][0]
        conn.upsertEdge("User", uid, "OWNS_ACCOUNT", "BankAccount", acc, {"since": "2023-01"})

    # --- SENT_TO edges (Money transfers) ---
    # Fraud ring: circular money transfers (F001 -> F002 -> F003 -> F004 -> F005 -> F001)
    fraud_transfers = [
        ("F001", "F002", 5000.0, "TX-FR-001", "2024-03-01"),
        ("F002", "F003", 4800.0, "TX-FR-002", "2024-03-02"),
        ("F003", "F004", 4600.0, "TX-FR-003", "2024-03-03"),
        ("F004", "F005", 4400.0, "TX-FR-004", "2024-03-04"),
        ("F005", "F001", 4200.0, "TX-FR-005", "2024-03-05"),
        # Additional suspicious transfers
        ("F001", "F003", 3000.0, "TX-FR-006", "2024-03-06"),
        ("F002", "F005", 2500.0, "TX-FR-007", "2024-03-07"),
        ("F003", "F001", 6000.0, "TX-FR-008", "2024-03-08"),
        ("F004", "F002", 1800.0, "TX-FR-009", "2024-03-09"),
    ]

    for sender, receiver, amount, tx_id, ts in fraud_transfers:
        conn.upsertEdge("User", sender, "SENT_TO", "User", receiver, {
            "amount": amount,
            "tx_id": tx_id,
            "timestamp_val": ts,
        })

    # Legit transfers (normal patterns)
    legit_transfers = [
        ("L001", "L002", 250.0, "TX-LG-001", "2024-02-15"),
        ("L003", "L004", 100.0, "TX-LG-002", "2024-02-20"),
        ("L005", "L006", 500.0, "TX-LG-003", "2024-02-25"),
        ("L007", "L008", 75.0, "TX-LG-004", "2024-03-01"),
        ("L009", "L010", 200.0, "TX-LG-005", "2024-03-05"),
        ("L002", "L001", 250.0, "TX-LG-006", "2024-03-10"),
        # Some legit users interacting with fraud ring (unknowingly)
        ("L001", "F001", 150.0, "TX-LG-007", "2024-03-12"),
        ("L005", "F003", 300.0, "TX-LG-008", "2024-03-14"),
    ]

    for sender, receiver, amount, tx_id, ts in legit_transfers:
        conn.upsertEdge("User", sender, "SENT_TO", "User", receiver, {
            "amount": amount,
            "tx_id": tx_id,
            "timestamp_val": ts,
        })

    print("[DataLoader] ✅ Sample data loaded successfully!")
    print(f"  - {len(all_users)} users ({len(fraud_users)} fraudsters, {len(legit_users)} legitimate)")
    print(f"  - {len(phones)} phones")
    print(f"  - {len(devices)} devices")
    print(f"  - {len(accounts)} bank accounts")
    print(f"  - {len(fraud_transfers)} fraud transfers")
    print(f"  - {len(legit_transfers)} legitimate transfers")

    return True


if __name__ == "__main__":
    load_sample_data()
