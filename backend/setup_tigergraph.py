"""
TigerGraph Schema Setup Script.
Run this once to create the graph schema, install queries, and load sample data.
"""

import pyTigerGraph as tg
import time
import sys
import os

TG_HOST = os.getenv("TG_HOST", "http://localhost")
TG_REST_PORT = os.getenv("TG_REST_PORT", "9000")
TG_GS_PORT = os.getenv("TG_GS_PORT", "14240")
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")


def setup_schema():
    """Create graph schema using GSQL."""
    print("=" * 60)
    print("  GraphGuard AI — TigerGraph Schema Setup")
    print("=" * 60)

    # Connect without graph first
    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
    )

    print("\n[1/4] Creating graph schema...")

    schema_gsql = """
    DROP ALL

    CREATE VERTEX User (PRIMARY_ID uid STRING, name STRING, email STRING, created_at STRING, is_flagged BOOL) WITH primary_id_as_attribute="true"
    CREATE VERTEX Phone (PRIMARY_ID number STRING, carrier STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX BankAccount (PRIMARY_ID account_number STRING, bank_name STRING, balance DOUBLE DEFAULT 0) WITH primary_id_as_attribute="true"
    CREATE VERTEX Device (PRIMARY_ID device_id STRING, device_type STRING, os STRING) WITH primary_id_as_attribute="true"

    CREATE DIRECTED EDGE HAS_PHONE (FROM User, TO Phone, since STRING)
    CREATE DIRECTED EDGE OWNS_ACCOUNT (FROM User, TO BankAccount, since STRING)
    CREATE DIRECTED EDGE USES_DEVICE (FROM User, TO Device, last_used STRING)
    CREATE DIRECTED EDGE SENT_TO (FROM User, TO User, amount DOUBLE, tx_id STRING, timestamp_val STRING)

    CREATE GRAPH FraudGraph (User, Phone, BankAccount, Device, HAS_PHONE, OWNS_ACCOUNT, USES_DEVICE, SENT_TO)
    """

    try:
        result = conn.gsql(schema_gsql)
        print(result)
    except Exception as e:
        print(f"Schema creation note: {e}")
        print("Attempting to continue...")

    # Wait for graph to be ready
    print("\n[2/4] Waiting for graph to be ready...")
    time.sleep(5)

    # Reconnect with graph
    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
        graphname="FraudGraph",
    )

    try:
        secret = conn.createSecret()
        conn.getToken(secret)
    except Exception:
        pass

    print("\n[3/4] Installing GSQL queries...")
    install_queries(conn)

    print("\n[4/4] Loading sample data...")
    load_data(conn)

    print("\n" + "=" * 60)
    print("  ✅ Setup complete! GraphGuard AI is ready.")
    print("=" * 60)


def install_queries(conn):
    """Install all fraud detection queries."""

    # Query: get_graph_data - returns all nodes and edges for visualization
    q_graph_data = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY get_graph_data() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING id, STRING node_type, STRING label, BOOL flagged> NodeInfo;
      TYPEDEF TUPLE<STRING source_node, STRING target_node, STRING edge_type, STRING label> EdgeInfo;
      ListAccum<NodeInfo> @@nodes;
      ListAccum<EdgeInfo> @@edges;

      users = {User.*};
      r1 = SELECT u FROM users:u
           ACCUM @@nodes += NodeInfo(u.uid, "User", u.name, u.is_flagged);

      r2 = SELECT p FROM users:u -(HAS_PHONE:e)-> Phone:p
           ACCUM
             @@nodes += NodeInfo(p.number, "Phone", p.number, false),
             @@edges += EdgeInfo(u.uid, p.number, "HAS_PHONE", "has_phone");

      r3 = SELECT d FROM users:u -(USES_DEVICE:e)-> Device:d
           ACCUM
             @@nodes += NodeInfo(d.device_id, "Device", d.device_type, false),
             @@edges += EdgeInfo(u.uid, d.device_id, "USES_DEVICE", "uses_device");

      r4 = SELECT a FROM users:u -(OWNS_ACCOUNT:e)-> BankAccount:a
           ACCUM
             @@nodes += NodeInfo(a.account_number, "BankAccount", a.bank_name, false),
             @@edges += EdgeInfo(u.uid, a.account_number, "OWNS_ACCOUNT", "owns_account");

      r5 = SELECT t FROM users:u -(SENT_TO:e)-> User:t
           ACCUM @@edges += EdgeInfo(u.uid, t.uid, "SENT_TO", "$" + to_string(e.amount));

      PRINT @@nodes AS nodes;
      PRINT @@edges AS edges;
    }
    INSTALL QUERY get_graph_data
    """

    # Query: check_user_risk
    q_check_user = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY check_user_risk(STRING user_id) FOR GRAPH FraudGraph {
      SumAccum<INT> @@shared_device_count;
      SumAccum<INT> @@shared_phone_count;
      SumAccum<INT> @@sent_to_count;
      SumAccum<INT> @@received_from_count;
      SumAccum<DOUBLE> @@total_sent;
      SumAccum<DOUBLE> @@total_received;
      SetAccum<STRING> @@connected_flagged_users;
      OrAccum @@is_flagged;
      MaxAccum<STRING> @@user_name;

      start = {User.*};
      user_node = SELECT u FROM start:u WHERE u.uid == user_id
                  POST-ACCUM @@is_flagged += u.is_flagged, @@user_name += u.name;

      // Check shared devices
      user_devices = SELECT d FROM user_node:u -(USES_DEVICE)-> Device:d;
      shared_users_d = SELECT u2 FROM user_devices:d -(reverse_USES_DEVICE)-> User:u2
                       WHERE u2.uid != user_id
                       POST-ACCUM @@shared_device_count += 1;

      // Check shared phones
      user_phones = SELECT p FROM user_node:u -(HAS_PHONE)-> Phone:p;
      shared_users_p = SELECT u2 FROM user_phones:p -(reverse_HAS_PHONE)-> User:u2
                       WHERE u2.uid != user_id
                       POST-ACCUM @@shared_phone_count += 1;

      // Check outgoing transactions
      sent = SELECT t FROM user_node:u -(SENT_TO:e)-> User:t
             ACCUM @@sent_to_count += 1, @@total_sent += e.amount;

      // Check incoming transactions
      all_users = {User.*};
      received = SELECT u2 FROM all_users:u2 -(SENT_TO:e)-> user_node:u
                 ACCUM @@received_from_count += 1, @@total_received += e.amount;

      // Check connections to flagged users
      flagged_via_tx = SELECT u2 FROM user_node:u -(SENT_TO)-> User:u2
                       WHERE u2.is_flagged == true
                       ACCUM @@connected_flagged_users += u2.uid;

      flagged_via_dev = SELECT u3 FROM user_devices:d -(reverse_USES_DEVICE)-> User:u3
                        WHERE u3.is_flagged == true AND u3.uid != user_id
                        ACCUM @@connected_flagged_users += u3.uid;

      PRINT @@user_name AS user_name;
      PRINT @@is_flagged AS is_flagged;
      PRINT @@shared_device_count AS shared_device_count;
      PRINT @@shared_phone_count AS shared_phone_count;
      PRINT @@sent_to_count AS sent_to_count;
      PRINT @@received_from_count AS received_from_count;
      PRINT @@total_sent AS total_sent;
      PRINT @@total_received AS total_received;
      PRINT @@connected_flagged_users AS connected_flagged_users;
    }
    INSTALL QUERY check_user_risk
    """

    # Query: find_connections from phone
    q_find_connections = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY find_connections(STRING phone_num) FOR GRAPH FraudGraph {
      SetAccum<STRING> @@connected_users;
      SetAccum<STRING> @@connected_phones;
      SetAccum<STRING> @@connected_devices;
      SetAccum<STRING> @@connected_accounts;

      start = {Phone.*};
      phones = SELECT p FROM start:p WHERE p.number == phone_num;

      users1 = SELECT u FROM phones:p -(reverse_HAS_PHONE)-> User:u
               ACCUM @@connected_users += u.uid;

      phones2 = SELECT ph FROM users1:u -(HAS_PHONE)-> Phone:ph
                ACCUM @@connected_phones += ph.number;

      devices2 = SELECT d FROM users1:u -(USES_DEVICE)-> Device:d
                 ACCUM @@connected_devices += d.device_id;

      accounts2 = SELECT a FROM users1:u -(OWNS_ACCOUNT)-> BankAccount:a
                  ACCUM @@connected_accounts += a.account_number;

      users3 = SELECT u FROM devices2:d -(reverse_USES_DEVICE)-> User:u
               ACCUM @@connected_users += u.uid;

      PRINT @@connected_users AS connected_users;
      PRINT @@connected_phones AS connected_phones;
      PRINT @@connected_devices AS connected_devices;
      PRINT @@connected_accounts AS connected_accounts;
    }
    INSTALL QUERY find_connections
    """

    # Query: detect_shared_devices
    q_shared_devices = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY detect_shared_devices() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING dev_id, STRING dev_type, INT user_count> SharedDeviceInfo;
      ListAccum<SharedDeviceInfo> @@shared_devices;
      SetAccum<STRING> @user_list;

      start = {Device.*};
      result = SELECT d FROM start:d -(reverse_USES_DEVICE)-> User:u
               ACCUM d.@user_list += u.uid
               POST-ACCUM
                 CASE WHEN d.@user_list.size() > 1 THEN
                   @@shared_devices += SharedDeviceInfo(d.device_id, d.device_type, d.@user_list.size())
                 END;

      PRINT @@shared_devices AS shared_devices;
    }
    INSTALL QUERY detect_shared_devices
    """

    # Query: detect_money_loops
    q_money_loops = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY detect_money_loops() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING user_a, STRING user_b, STRING user_c> MoneyLoop;
      ListAccum<MoneyLoop> @@loops;
      SetAccum<STRING> @@seen;

      start = {User.*};
      result = SELECT a FROM start:a -(SENT_TO)-> User:b -(SENT_TO)-> User:c -(SENT_TO)-> User:a2
               WHERE a == a2 AND a != b AND b != c AND a != c
               ACCUM
                 STRING key = a.uid + "-" + b.uid + "-" + c.uid,
                 CASE WHEN NOT @@seen.contains(key) THEN
                   @@loops += MoneyLoop(a.uid, b.uid, c.uid),
                   @@seen += key
                 END;

      PRINT @@loops AS money_loops;
    }
    INSTALL QUERY detect_money_loops
    """

    # Query: detect_phone_reuse
    q_phone_reuse = """
    USE GRAPH FraudGraph
    CREATE OR REPLACE QUERY detect_phone_reuse() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING phone_number, STRING carrier, INT user_count> PhoneReuse;
      ListAccum<PhoneReuse> @@reused_phones;
      SetAccum<STRING> @user_list;

      start = {Phone.*};
      result = SELECT p FROM start:p -(reverse_HAS_PHONE)-> User:u
               ACCUM p.@user_list += u.uid
               POST-ACCUM
                 CASE WHEN p.@user_list.size() > 1 THEN
                   @@reused_phones += PhoneReuse(p.number, p.carrier, p.@user_list.size())
                 END;

      PRINT @@reused_phones AS reused_phones;
    }
    INSTALL QUERY detect_phone_reuse
    """

    queries = [
        ("get_graph_data", q_graph_data),
        ("check_user_risk", q_check_user),
        ("find_connections", q_find_connections),
        ("detect_shared_devices", q_shared_devices),
        ("detect_money_loops", q_money_loops),
        ("detect_phone_reuse", q_phone_reuse),
    ]

    for name, gsql in queries:
        try:
            print(f"  Installing {name}...")
            result = conn.gsql(gsql)
            print(f"    ✅ {name} installed")
        except Exception as e:
            print(f"    ⚠️ {name}: {e}")


def load_data(conn):
    """Load sample fraud data."""
    print("  Loading vertices...")

    # FRAUD RING USERS
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

    for uid, name, email, created, flagged in all_users:
        conn.upsertVertex("User", uid, {
            "name": name, "email": email, "created_at": created, "is_flagged": flagged
        })

    # PHONES
    phones = [
        ("+1-555-0101", "BurnerNet"), ("+1-555-0102", "BurnerNet"), ("+1-555-0103", "ShadowMobile"),
        ("+1-555-1001", "Verizon"), ("+1-555-1002", "AT&T"), ("+1-555-1003", "T-Mobile"),
        ("+1-555-1004", "Verizon"), ("+1-555-1005", "AT&T"), ("+1-555-1006", "T-Mobile"),
        ("+1-555-1007", "Verizon"), ("+1-555-1008", "AT&T"), ("+1-555-1009", "T-Mobile"),
        ("+1-555-1010", "Verizon"), ("+1-555-1011", "AT&T"), ("+1-555-1012", "T-Mobile"),
        ("+1-555-1013", "Verizon"), ("+1-555-1014", "AT&T"), ("+1-555-1015", "T-Mobile"),
    ]
    for number, carrier in phones:
        conn.upsertVertex("Phone", number, {"carrier": carrier})

    # DEVICES
    devices = [
        ("DEV-X001", "Android", "Android 12"), ("DEV-X002", "Laptop", "Windows 11"),
        ("DEV-L001", "iPhone", "iOS 17"), ("DEV-L002", "Android", "Android 14"),
        ("DEV-L003", "iPhone", "iOS 16"), ("DEV-L004", "Android", "Android 13"),
        ("DEV-L005", "iPhone", "iOS 17"), ("DEV-L006", "Android", "Android 14"),
        ("DEV-L007", "iPad", "iPadOS 17"), ("DEV-L008", "Android", "Android 13"),
        ("DEV-L009", "iPhone", "iOS 17"), ("DEV-L010", "Laptop", "macOS 14"),
        ("DEV-L011", "iPhone", "iOS 16"), ("DEV-L012", "Android", "Android 14"),
        ("DEV-L013", "iPhone", "iOS 17"), ("DEV-L014", "Android", "Android 13"),
        ("DEV-L015", "Laptop", "Windows 11"),
    ]
    for dev_id, dev_type, dev_os in devices:
        conn.upsertVertex("Device", dev_id, {"device_type": dev_type, "os": dev_os})

    # BANK ACCOUNTS
    accounts = [
        ("ACC-F001", "ShadowBank", 15200.0), ("ACC-F002", "ShadowBank", 8900.0),
        ("ACC-F003", "CryptoPay", 22000.0), ("ACC-F004", "ShadowBank", 5600.0),
        ("ACC-F005", "CryptoPay", 31000.0),
        ("ACC-L001", "Chase", 45000.0), ("ACC-L002", "BankOfAmerica", 32000.0),
        ("ACC-L003", "Wells Fargo", 28000.0), ("ACC-L004", "Chase", 55000.0),
        ("ACC-L005", "HDFC Bank", 41000.0), ("ACC-L006", "Citi Bank", 19000.0),
        ("ACC-L007", "Chase", 67000.0), ("ACC-L008", "BankOfAmerica", 23000.0),
        ("ACC-L009", "Wells Fargo", 38000.0), ("ACC-L010", "Chase", 52000.0),
        ("ACC-L011", "HDFC Bank", 29000.0), ("ACC-L012", "Citi Bank", 44000.0),
        ("ACC-L013", "Chase", 36000.0), ("ACC-L014", "BankOfAmerica", 27000.0),
        ("ACC-L015", "Wells Fargo", 48000.0),
    ]
    for acc_num, bank, balance in accounts:
        conn.upsertVertex("BankAccount", acc_num, {"bank_name": bank, "balance": balance})

    print("  Loading edges...")

    # HAS_PHONE - fraud ring shares phones
    phone_edges = [
        ("F001", "+1-555-0101"), ("F002", "+1-555-0101"), ("F003", "+1-555-0101"),
        ("F003", "+1-555-0102"), ("F004", "+1-555-0102"), ("F005", "+1-555-0103"),
    ]
    for i in range(15):
        uid = f"L{str(i+1).zfill(3)}"
        phone_edges.append((uid, phones[3 + i][0]))

    for uid, phone in phone_edges:
        conn.upsertEdge("User", uid, "HAS_PHONE", "Phone", phone, {"since": "2024-01"})

    # USES_DEVICE - fraud ring shares devices
    device_edges = [
        ("F001", "DEV-X001"), ("F002", "DEV-X001"), ("F003", "DEV-X002"),
        ("F004", "DEV-X001"), ("F005", "DEV-X002"),
    ]
    for i in range(15):
        uid = f"L{str(i+1).zfill(3)}"
        device_edges.append((uid, devices[2 + i][0]))

    for uid, dev in device_edges:
        conn.upsertEdge("User", uid, "USES_DEVICE", "Device", dev, {"last_used": "2024-03"})

    # OWNS_ACCOUNT
    for i, (uid, *_) in enumerate(all_users):
        conn.upsertEdge("User", uid, "OWNS_ACCOUNT", "BankAccount", accounts[i][0], {"since": "2023-01"})

    # SENT_TO - circular fraud transfers
    transfers = [
        ("F001", "F002", 5000.0, "TX-FR-001", "2024-03-01"),
        ("F002", "F003", 4800.0, "TX-FR-002", "2024-03-02"),
        ("F003", "F004", 4600.0, "TX-FR-003", "2024-03-03"),
        ("F004", "F005", 4400.0, "TX-FR-004", "2024-03-04"),
        ("F005", "F001", 4200.0, "TX-FR-005", "2024-03-05"),
        ("F001", "F003", 3000.0, "TX-FR-006", "2024-03-06"),
        ("F002", "F005", 2500.0, "TX-FR-007", "2024-03-07"),
        ("F003", "F001", 6000.0, "TX-FR-008", "2024-03-08"),
        ("F004", "F002", 1800.0, "TX-FR-009", "2024-03-09"),
        ("L001", "L002", 250.0, "TX-LG-001", "2024-02-15"),
        ("L003", "L004", 100.0, "TX-LG-002", "2024-02-20"),
        ("L005", "L006", 500.0, "TX-LG-003", "2024-02-25"),
        ("L007", "L008", 75.0, "TX-LG-004", "2024-03-01"),
        ("L009", "L010", 200.0, "TX-LG-005", "2024-03-05"),
        ("L002", "L001", 250.0, "TX-LG-006", "2024-03-10"),
        ("L001", "F001", 150.0, "TX-LG-007", "2024-03-12"),
        ("L005", "F003", 300.0, "TX-LG-008", "2024-03-14"),
    ]

    for sender, receiver, amount, tx_id, ts in transfers:
        conn.upsertEdge("User", sender, "SENT_TO", "User", receiver, {
            "amount": amount, "tx_id": tx_id, "timestamp_val": ts,
        })

    print(f"  ✅ Loaded {len(all_users)} users, {len(phones)} phones, {len(devices)} devices, {len(accounts)} accounts")
    print(f"  ✅ Loaded {len(transfers)} transactions")


if __name__ == "__main__":
    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
        graphname="FraudGraph"
    )
    print("Installing queries...")
    install_queries(conn)
    print("Loading data...")
    load_data(conn)
    print("Setup complete!")

