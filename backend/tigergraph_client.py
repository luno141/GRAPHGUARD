"""
TigerGraph Client for GraphGuard AI.

Handles connection, schema creation, data loading, and query execution.
Uses pyTigerGraph for communication with TigerGraph database.
"""

import pyTigerGraph as tg
import json
import os


# TigerGraph connection config
TG_HOST = os.getenv("TG_HOST", "http://localhost")
TG_REST_PORT = os.getenv("TG_REST_PORT", "9000")
TG_GS_PORT = os.getenv("TG_GS_PORT", "14240")
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")
TG_GRAPH = os.getenv("TG_GRAPH", "FraudGraph")


class TigerGraphClient:
    def __init__(self):
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish connection to TigerGraph."""
        try:
            self.conn = tg.TigerGraphConnection(
                host=TG_HOST,
                restppPort=TG_REST_PORT,
                gsPort=TG_GS_PORT,
                username=TG_USERNAME,
                password=TG_PASSWORD,
                graphname=TG_GRAPH,
            )
            # Get API token
            try:
                self.conn.getToken(self.conn.createSecret())
            except Exception:
                # Token may not be needed for community edition
                pass
            print(f"[TigerGraph] Connected to {TG_HOST}, graph: {TG_GRAPH}")
        except Exception as e:
            print(f"[TigerGraph] Connection error: {e}")
            self.conn = None

    def is_connected(self) -> bool:
        """Check if connected to TigerGraph."""
        if self.conn is None:
            return False
        try:
            self.conn.echo()
            return True
        except Exception:
            return False

    def run_query(self, query_name: str, params: dict = None) -> dict:
        """Run an installed GSQL query."""
        try:
            result = self.conn.runInstalledQuery(query_name, params=params or {})
            return result
        except Exception as e:
            print(f"[TigerGraph] Query error ({query_name}): {e}")
            return []

    def get_graph_data(self) -> dict:
        """Get full graph visualization data."""
        result = self.run_query("get_graph_data")
        nodes = []
        edges = []
        seen_nodes = set()
        
        for item in result:
            if "nodes" in item:
                for n in item["nodes"]:
                    if n["id"] not in seen_nodes:
                        nodes.append(n)
                        seen_nodes.add(n["id"])
            if "edges" in item:
                for e in item["edges"]:
                    edges.append(e)
        
        return {"nodes": nodes, "edges": edges}

    def check_user_risk(self, user_id: str) -> dict:
        """Get risk signals for a specific user."""
        result = self.run_query("check_user_risk", {"user_id": user_id})
        
        signals = {
            "user_name": "",
            "is_flagged": False,
            "shared_device_count": 0,
            "shared_phone_count": 0,
            "sent_to_count": 0,
            "received_from_count": 0,
            "total_sent": 0.0,
            "total_received": 0.0,
            "connected_flagged_users": [],
        }
        
        for item in result:
            for key in signals:
                if key in item:
                    signals[key] = item[key]
        
        return signals

    def find_connections(self, phone_num: str) -> dict:
        """Find all connections from a phone number."""
        result = self.run_query("find_connections", {"phone_num": phone_num})
        
        connections = {
            "connected_users": [],
            "connected_phones": [],
            "connected_devices": [],
            "connected_accounts": [],
        }
        
        for item in result:
            for key in connections:
                if key in item:
                    connections[key] = item[key]
        
        return connections

    def detect_shared_devices(self) -> list:
        """Detect users sharing devices."""
        result = self.run_query("detect_shared_devices")
        for item in result:
            if "shared_devices" in item:
                return item["shared_devices"]
        return []

    def detect_money_loops(self) -> list:
        """Detect circular money transfers."""
        result = self.run_query("detect_money_loops")
        for item in result:
            if "money_loops" in item:
                return item["money_loops"]
        return []

    def detect_phone_reuse(self) -> list:
        """Detect phone numbers shared across users."""
        result = self.run_query("detect_phone_reuse")
        for item in result:
            if "reused_phones" in item:
                return item["reused_phones"]
        return []

    def get_vertex_count(self, vertex_type: str) -> int:
        """Get count of vertices of a specific type."""
        try:
            return self.conn.getVertexCount(vertex_type)
        except Exception:
            return 0

    def get_edge_count(self, edge_type: str) -> int:
        """Get count of edges of a specific type."""
        try:
            counts = self.conn.getEdgeCount(edge_type)
            if isinstance(counts, dict):
                return int(counts.get(edge_type, 0))
            return int(counts or 0)
        except Exception:
            return 0

    def get_transaction_count(self) -> int:
        """
        Get total transaction count.

        Some local setups model transactions as `SENT_TO` edges instead of
        dedicated `Transaction` vertices, so we fall back to edge counts.
        """
        transaction_vertices = self.get_vertex_count("Transaction")
        if transaction_vertices > 0:
            return transaction_vertices
        return self.get_edge_count("SENT_TO")

    def get_all_users(self) -> list:
        """Get all user vertices."""
        try:
            vertices = self.conn.getVertices("User")
            users = []
            for v in vertices:
                users.append({
                    "uid": v["v_id"],
                    "name": v["attributes"].get("name", ""),
                    "email": v["attributes"].get("email", ""),
                    "is_flagged": v["attributes"].get("is_flagged", False),
                })
            return users
        except Exception as e:
            print(f"[TigerGraph] Error getting users: {e}")
            return []

    def get_all_phones(self) -> list:
        """Get all phone vertices."""
        try:
            vertices = self.conn.getVertices("Phone")
            phones = []
            for v in vertices:
                phones.append({
                    "number": v["v_id"],
                    "carrier": v["attributes"].get("carrier", ""),
                })
            return phones
        except Exception as e:
            print(f"[TigerGraph] Error getting phones: {e}")
            return []
