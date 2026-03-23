
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
    print("=" * 60)
    print("  GraphGuard AI — Full TigerGraph Override Setup")
    print("=" * 60)

    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
    )

    schema_gsql = """
    DROP ALL

    CREATE VERTEX User (PRIMARY_ID uid STRING, name STRING, email STRING, created_at STRING, is_flagged BOOL) WITH primary_id_as_attribute="true"
    CREATE VERTEX Phone (PRIMARY_ID number STRING, carrier STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX BankAccount (PRIMARY_ID account_number STRING, bank_name STRING, balance DOUBLE DEFAULT 0) WITH primary_id_as_attribute="true"
    CREATE VERTEX Device (PRIMARY_ID device_id STRING, device_type STRING, os STRING) WITH primary_id_as_attribute="true"

    CREATE DIRECTED EDGE HAS_PHONE (FROM User, TO Phone, since STRING) WITH REVERSE_EDGE="reverse_HAS_PHONE"
    CREATE DIRECTED EDGE OWNS_ACCOUNT (FROM User, TO BankAccount, since STRING) WITH REVERSE_EDGE="reverse_OWNS_ACCOUNT"
    CREATE DIRECTED EDGE USES_DEVICE (FROM User, TO Device, last_used STRING) WITH REVERSE_EDGE="reverse_USES_DEVICE"
    CREATE DIRECTED EDGE SENT_TO (FROM User, TO User, amount DOUBLE, tx_id STRING, timestamp_val STRING) WITH REVERSE_EDGE="reverse_SENT_TO"

    CREATE GRAPH FraudGraph (User, Phone, BankAccount, Device, HAS_PHONE, OWNS_ACCOUNT, USES_DEVICE, SENT_TO)
    """

    try:
        print("\n[1/4] Dropping and re-creating schema (with REVERSE_EDGEs)...")
        print(conn.gsql(schema_gsql))
    except Exception as e:
        print(f"Schema creation note: {e}")

    print("\n[2/4] Waiting for graph to compile (can take 2 minutes)...")
    time.sleep(30) # GPE/GSE start takes long
    
    conn = tg.TigerGraphConnection(
        host=TG_HOST,
        restppPort=TG_REST_PORT,
        gsPort=TG_GS_PORT,
        username=TG_USERNAME,
        password=TG_PASSWORD,
        graphname="FraudGraph",
    )
    
    # Simple wait polling loop
    for _ in range(10):
        try:
             conn.getVertexCount("User")
             break
        except Exception:
             time.sleep(10)

    print("\n[3/4] Installing GSQL queries...")
    install_queries(conn)

    print("\n[4/4] Loading sample data...")
    load_data(conn)


def install_queries(conn):
    q_all = """
    USE GRAPH FraudGraph

    CREATE OR REPLACE QUERY get_graph_data() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING id, STRING node_type, STRING label, BOOL flagged> NodeInfo;
      TYPEDEF TUPLE<STRING source_node, STRING target_node, STRING edge_type, STRING label> EdgeInfo;
      ListAccum<NodeInfo> @@nodes;
      ListAccum<EdgeInfo> @@edges;

      users = {User.*};
      r1 = SELECT u FROM users:u
           ACCUM @@nodes += NodeInfo(u.uid, "User", u.name, u.is_flagged);

      r2 = SELECT p FROM users:u -(HAS_PHONE:e)- Phone:p
           ACCUM
             @@nodes += NodeInfo(p.number, "Phone", p.number, false),
             @@edges += EdgeInfo(u.uid, p.number, "HAS_PHONE", "has_phone");

      r3 = SELECT d FROM users:u -(USES_DEVICE:e)- Device:d
           ACCUM
             @@nodes += NodeInfo(d.device_id, "Device", d.device_type, false),
             @@edges += EdgeInfo(u.uid, d.device_id, "USES_DEVICE", "uses_device");

      r4 = SELECT a FROM users:u -(OWNS_ACCOUNT:e)- BankAccount:a
           ACCUM
             @@nodes += NodeInfo(a.account_number, "BankAccount", a.bank_name, false),
             @@edges += EdgeInfo(u.uid, a.account_number, "OWNS_ACCOUNT", "owns_account");

      r5 = SELECT t FROM users:u -(SENT_TO:e)- User:t
           ACCUM @@edges += EdgeInfo(u.uid, t.uid, "SENT_TO", "$" + to_string(e.amount));

      PRINT @@nodes AS nodes;
      PRINT @@edges AS edges;
    }

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

      user_devices = SELECT d FROM user_node:u -(USES_DEVICE)- Device:d;
      shared_users_d = SELECT u2 FROM user_devices:d -(reverse_USES_DEVICE)- User:u2
                       WHERE u2.uid != user_id
                       POST-ACCUM @@shared_device_count += 1;

      user_phones = SELECT p FROM user_node:u -(HAS_PHONE)- Phone:p;
      shared_users_p = SELECT u2 FROM user_phones:p -(reverse_HAS_PHONE)- User:u2
                       WHERE u2.uid != user_id
                       POST-ACCUM @@shared_phone_count += 1;

      sent = SELECT t FROM user_node:u -(SENT_TO:e)- User:t
             ACCUM @@sent_to_count += 1, @@total_sent += e.amount;

      all_users = {User.*};
      received = SELECT u2 FROM all_users:u2 -(SENT_TO:e)- user_node:u
                 ACCUM @@received_from_count += 1, @@total_received += e.amount;

      flagged_via_tx = SELECT u2 FROM user_node:u -(SENT_TO)- User:u2
                       WHERE u2.is_flagged == true
                       ACCUM @@connected_flagged_users += u2.uid;

      flagged_via_dev = SELECT u3 FROM user_devices:d -(reverse_USES_DEVICE)- User:u3
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

    CREATE OR REPLACE QUERY find_connections(STRING phone_num) FOR GRAPH FraudGraph {
      SetAccum<STRING> @@connected_users;
      SetAccum<STRING> @@connected_phones;
      SetAccum<STRING> @@connected_devices;
      SetAccum<STRING> @@connected_accounts;

      start = {Phone.*};
      phones = SELECT p FROM start:p WHERE p.number == phone_num;

      users1 = SELECT u FROM phones:p -(reverse_HAS_PHONE)- User:u
               ACCUM @@connected_users += u.uid;

      phones2 = SELECT ph FROM users1:u -(HAS_PHONE)- Phone:ph
                ACCUM @@connected_phones += ph.number;

      devices2 = SELECT d FROM users1:u -(USES_DEVICE)- Device:d
                 ACCUM @@connected_devices += d.device_id;

      accounts2 = SELECT a FROM users1:u -(OWNS_ACCOUNT)- BankAccount:a
                  ACCUM @@connected_accounts += a.account_number;

      users3 = SELECT u FROM devices2:d -(reverse_USES_DEVICE)- User:u
               ACCUM @@connected_users += u.uid;

      PRINT @@connected_users AS connected_users;
      PRINT @@connected_phones AS connected_phones;
      PRINT @@connected_devices AS connected_devices;
      PRINT @@connected_accounts AS connected_accounts;
    }

    CREATE OR REPLACE QUERY detect_shared_devices() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING dev_id, STRING dev_type, INT user_count> SharedDeviceInfo;
      ListAccum<SharedDeviceInfo> @@shared_devices;
      SetAccum<STRING> @user_list;

      start = {Device.*};
      result = SELECT d FROM start:d -(reverse_USES_DEVICE)- User:u
               ACCUM d.@user_list += u.uid
               POST-ACCUM
                 CASE WHEN d.@user_list.size() > 1 THEN
                   @@shared_devices += SharedDeviceInfo(d.device_id, d.device_type, d.@user_list.size())
                 END;

      PRINT @@shared_devices AS shared_devices;
    }

    CREATE OR REPLACE QUERY detect_money_loops() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING user_a, STRING user_b, STRING user_c> MoneyLoop;
      ListAccum<MoneyLoop> @@loops;
      SetAccum<STRING> @@seen;

      start = {User.*};
      result = SELECT a FROM start:a -(SENT_TO)- User:b -(SENT_TO)- User:c -(SENT_TO)- User:a2
               WHERE a == a2 AND a != b AND b != c AND a != c
               ACCUM
                 STRING key = a.uid + "-" + b.uid + "-" + c.uid,
                 CASE WHEN NOT @@seen.contains(key) THEN
                   @@loops += MoneyLoop(a.uid, b.uid, c.uid),
                   @@seen += key
                 END;

      PRINT @@loops AS money_loops;
    }

    CREATE OR REPLACE QUERY detect_phone_reuse() FOR GRAPH FraudGraph {
      TYPEDEF TUPLE<STRING phone_number, STRING carrier, INT user_count> PhoneReuse;
      ListAccum<PhoneReuse> @@reused_phones;
      SetAccum<STRING> @user_list;

      start = {Phone.*};
      result = SELECT p FROM start:p -(reverse_HAS_PHONE)- User:u
               ACCUM p.@user_list += u.uid
               POST-ACCUM
                 CASE WHEN p.@user_list.size() > 1 THEN
                   @@reused_phones += PhoneReuse(p.number, p.carrier, p.@user_list.size())
                 END;

      PRINT @@reused_phones AS reused_phones;
    }

    INSTALL QUERY ALL
    """
    conn.gsql(q_all)
    print("Queries Re-compiled!")


def load_data(conn):
    fraud_users = [
        ("F001", "Viktor Petrov", "vpetrov@darkmail.com", "2024-01-15", True),
        ("F002", "Elena Kozlov", "ekozlov@tempmail.net", "2024-01-16", True),
        ("F003", "Dmitri Volkov", "dvolkov@fakebox.io", "2024-01-17", True),
        ("F004", "Anya Sokolov", "asokolov@burner.org", "2024-01-18", True),
        ("F005", "Boris Ivanov", "bivanov@shadow.cc", "2024-01-19", True),
    ]
    legit_users = [("L001", "Sarah Johnson", "sarah.j@gmail.com", "2023-06-01", False), ("L002", "Michael Chen", "m.chen@outlook.com", "2023-07-15", False)]
    all_users = fraud_users + legit_users

    for uid, name, email, created, flagged in all_users:
        conn.upsertVertex("User", uid, {"name": name, "email": email, "created_at": created, "is_flagged": flagged})

    phones = [("+1-555-0101", "BurnerNet"), ("+1-555-0102", "BurnerNet"), ("+1-555-0103", "ShadowMobile"), ("+1-555-1001", "Verizon"), ("+1-555-1002", "AT&T")]
    for number, carrier in phones:
        conn.upsertVertex("Phone", number, {"carrier": carrier})

    devices = [("DEV-X001", "Android", "Android 12"), ("DEV-X002", "Laptop", "Windows 11"), ("DEV-L001", "iPhone", "iOS 17")]
    for dev_id, dev_type, dev_os in devices:
        conn.upsertVertex("Device", dev_id, {"device_type": dev_type, "os": dev_os})

    accounts = [("ACC-F001", "ShadowBank", 15200.0), ("ACC-F002", "ShadowBank", 8900.0), ("ACC-F003", "CryptoPay", 22000.0)]
    for acc_num, bank, balance in accounts:
        conn.upsertVertex("BankAccount", acc_num, {"bank_name": bank, "balance": balance})

    conn.upsertEdge("User", "F001", "HAS_PHONE", "Phone", "+1-555-0101", {"since": "2024-01"})
    conn.upsertEdge("User", "F002", "HAS_PHONE", "Phone", "+1-555-0101", {"since": "2024-01"})
    conn.upsertEdge("User", "F003", "HAS_PHONE", "Phone", "+1-555-0101", {"since": "2024-01"})
    conn.upsertEdge("User", "F003", "HAS_PHONE", "Phone", "+1-555-0102", {"since": "2024-01"})

    conn.upsertEdge("User", "F001", "USES_DEVICE", "Device", "DEV-X001", {"last_used": "2024-03"})
    conn.upsertEdge("User", "F002", "USES_DEVICE", "Device", "DEV-X001", {"last_used": "2024-03"})
    conn.upsertEdge("User", "F003", "USES_DEVICE", "Device", "DEV-X002", {"last_used": "2024-03"})

    conn.upsertEdge("User", "F001", "SENT_TO", "User", "F002", {"amount": 5000.0, "tx_id": "TX-1", "timestamp_val": "2024"})
    conn.upsertEdge("User", "F002", "SENT_TO", "User", "F003", {"amount": 5000.0, "tx_id": "TX-2", "timestamp_val": "2024"})
    conn.upsertEdge("User", "F003", "SENT_TO", "User", "F001", {"amount": 5000.0, "tx_id": "TX-3", "timestamp_val": "2024"})
    
    print("Graph Data loaded!")

if __name__ == "__main__":
    setup_schema()
