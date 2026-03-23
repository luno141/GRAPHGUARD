<p align="center">
  <img src="https://raw.githubusercontent.com/tigergraph/ecosystem/master/tigergraph_logo.png" alt="TigerGraph" width="150" />
</p>

# GraphGuard AI - TigerGraph Fraud Detection 🐯
> Stop sophisticated fraud rings with Deep Link Analysis and Sub-second Graph Queries on TigerGraph.

![Dashboard Preview](docs/dashboard.png) *(Add a screenshot here)*

## 💡 The Problem Statement
Modern financial fraud is no longer perpetrated by isolated actors. Today's threats come from **organized fraud rings** using complex networks of synthetic identities, burner phones, shared devices, and circular money transfers. 

Traditional relational databases and tabular rule engines identify fraud by looking at single rows. They **fail to detect the hidden connections** between entities. Analyzing "Who sent money to whom, who shares the same device as a flagged user, and who are they 3-hops connected to?" requires expensive multi-table joins that bring SQL databases to a crawl.

## 🔗 The Graph Use-Case (Why TigerGraph?)
GraphGuard AI solves this by adopting **TigerGraph** as its core intelligence engine. By modeling users, devices, bank accounts, and transactions as a Native Graph, we can achieve:

1. **Sub-second Deep Link Analysis:** Finding a 3-hop connection (User ➔ Phone ➔ User ➔ Device) executes in milliseconds in TigerGraph via GSQL.
2. **Pattern Matching:** Native graph queries easily detect shared device hubs, circular money trails, and phone number reuse.
3. **Graph-powered Risk Scoring:** We calculate real-time risks for any identity by measuring graph distance to known fraudulent actors.

### Graph Schema
- **Vertices:** `User`, `Phone`, `BankAccount`, `Device`
- **Edges (Directed):** 
  - `HAS_PHONE` (User ➔ Phone)
  - `OWNS_ACCOUNT` (User ➔ BankAccount)
  - `USES_DEVICE` (User ➔ Device)
  - `SENT_TO` (User ➔ User, holds `amount`)

## 🛠️ Implementation & Architecture
- **Database:** TigerGraph Database (Community Edition). Stores all relational entities and uses custom GSQL queries for network analytics.
- **Backend API:** FastAPI (Python), utilizing `pyTigerGraph` to execute queries over TigerGraph's REST++ API.
- **Frontend Dashboard:** React + Vite, featuring `react-cytoscapejs` for interactive node-edge visualization.

## 🚀 Impact
By switching to a graph-native architecture, investigations that used to take fraud analysts hours of manual cross-referencing now happen **instantly, autonomously, and visually.** Financial institutions can block funds in real-time before money leaves the network.

---

## 💻 Setup Instructions

### Prerequisites
1. Docker (to run TigerGraph locally containerized)
2. Python 3.10+
3. Node.js 18+

### Step 1: Start TigerGraph
Run TigerGraph locally via Docker:
```bash
docker run -d -p 9000:9000 -p 14240:14240 -p 14141:14141 --name tigergraph --ulimit nofile=1000000:1000000 tigergraph/tigergraph:latest
```
*Wait a couple of minutes for TigerGraph to fully boot.*

### Step 2: Install Schema & GSQL Queries
We provide an automated pyTigerGraph script that builds the schema, installs the GSQL REST endpoints, and loads mock fraud data.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the TigerGraph Override Script
python3 setup_tigergraph_v2.py
```
*(Note: Expect schema generation & query installation to take ~2 minutes. This runs `INSTALL QUERY ALL` natively inside TigerGraph).*

### Step 3: Run Backend API
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Run Frontend Viewer
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173`.

---

## 🔍 How TigerGraph is Used (GSQL Queries)
Within `queries_only.gsql`, you will find advanced TigerGraph V2 Syntax implementations:
- `find_connections(phone_num)`: Traverses reverse edges to find all users mapped to a phone, then recursively maps their accounts and devices out multiple hops.
- `detect_money_loops()`: Finds circular transfer rings (User A ➔ B ➔ C ➔ A) using multi-hop graph pattern matching.
- `detect_shared_devices()`: Accums and Groups users who share the identical `dev_id` MAC addresses.

## 📝 License
MIT
