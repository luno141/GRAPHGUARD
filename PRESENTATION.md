# GraphGuard AI - Hackathon Presentation Draft 🐯

*Use the text below to structure your PowerPoint (PPT) slides.*

---

## Slide 1: Title Slide
**Title:** GraphGuard AI
**Subtitle:** Stop sophisticated fraud rings with Deep Link Analysis & TigerGraph.
**Content:**
- Team Name: [Your Name/Team]
- Technology: TigerGraph Native Graph Intelligence, React, FastAPI.
*(Include team logos and TigerGraph logo)*

---

## Slide 2: The Problem Statement (Why Traditional Databases Fail)
**Title:** Modern Fraud is a Network Problem
**Content:**
- **The Threat:** Modern fraud isn't isolated. It involves organized rings utilizing synthetic identities, burner phones, shared devices, and circular money transfers.
- **The DB Bottleneck:** Traditional relational databases assess risk row-by-row. Finding connections like “Who shares a device with a known scammer, and who sent them money?” requires highly expensive, slow SQL `JOIN` operations.
- **The Impact:** When queries take minutes to run, money escapes the network before analysts can act.

---

## Slide 3: The Graph Use-Case (Why TigerGraph?)
**Title:** Enter TigerGraph: Real-time Threat Intelligence
**Content:**
- We modeled Identites, Phones, Devices, and Bank Accounts as **Vertices**, and their interactions as **Edges**.
- **Deep Link Analysis:** TigerGraph easily navigates 3-to-4 hop relationships (User ➔ Device ➔ User ➔ Phone ➔ User) in milliseconds.
- **Pattern Matching:** Via GSQL Native paths, we natively identify circular money money loops and device/phone-reuse syndicates without exporting data to external ML engines.

---

## Slide 4: Implementation Architecture
**Title:** System Architecture
**Content:**
- **Core Engine:** TigerGraph Database (Community Edition). Hosted via Docker.
- **Graph Schema:** `User`, `Phone`, `BankAccount`, `Device` vertices paired with directed reverse-edges (`HAS_PHONE`, `USES_DEVICE`, `SENT_TO`).
- **GSQL Brain:** Highly optimized custom `INSTALL QUERY` scripts that execute the logic inside the database natively.
- **API & UI:** Python FastAPI middleware converting TigerGraph GraphJSON to an interactive React + CytoscapeJS frontend graph visualization dashboard.

---

## Slide 5: Real World Impact
**Title:** Impact & Future 
**Content:**
- **Efficiency:** Turns hours of manual cross-referencing into less than 1-second of algorithmic traversal.
- **Preventative Action:** Unlocks the capability to block large-scale transactions in real-time as they attempt to pass through the network.
- **Accuracy:** The "guilt-by-association" GSQL queries immediately surface unflagged users acting as mules, directly cutting off network nodes.

---

## Slide 6: Demo Overview
**Title:** GraphGuard AI in Action
*(Take Screenshots or put your Demo Video here)*
**Highlights to show in video:**
1. Searching for an unflagged number and seeing its graph connections.
2. Cytoscape interactive graph rendering.
3. The real-time GSQL Fraud Signals (money loops, shared device counts) returned in milliseconds.
