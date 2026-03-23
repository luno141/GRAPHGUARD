"""Pydantic models for GraphGuard AI API."""
from pydantic import BaseModel, Field


class CheckNumberRequest(BaseModel):
    phone_number: str


class CheckUserRequest(BaseModel):
    user_id: str


class RiskSignals(BaseModel):
    shared_device_count: int = 0
    shared_phone_count: int = 0
    sent_to_count: int = 0
    received_from_count: int = 0
    total_sent: float = 0.0
    total_received: float = 0.0
    connected_flagged_users: list[str] = Field(default_factory=list)
    is_in_money_loop: bool = False
    is_flagged: bool = False


class RiskResult(BaseModel):
    user_id: str
    user_name: str
    risk_score: int  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    signals: RiskSignals
    explanation: list[str]
    connected_users: list[str] = Field(default_factory=list)
    connected_phones: list[str] = Field(default_factory=list)
    connected_devices: list[str] = Field(default_factory=list)
    connected_accounts: list[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    node_type: str
    label: str
    flagged: bool = False


class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: str
    label: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class FraudCluster(BaseModel):
    cluster_id: int
    users: list[str]
    shared_devices: list[str]
    shared_phones: list[str]
    risk_level: str


class HealthResponse(BaseModel):
    status: str
    tigergraph_connected: bool
    graph_name: str
