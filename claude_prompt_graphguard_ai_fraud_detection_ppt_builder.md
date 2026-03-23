# Claude Prompt: Build a Powerful PPT for GraphGuard AI

You are an expert startup pitch designer, technical storyteller, and presentation strategist.

Your task is to create a 12–14 slide PowerPoint presentation for a project called:

# GraphGuard AI — Fraud Intelligence System

The presentation should feel like a real startup or product pitch, not a college assignment. The tone should be modern, sharp, confident, and easy for judges, recruiters, or investors to understand.

The key theme of the presentation is:

“Fraud detection is a graph problem because malicious behavior emerges through relationships, not isolated events.”

The PPT should follow a narrative arc:
1. The problem
2. Why current systems fail
3. Why graph-based fraud detection is better
4. How GraphGuard AI works
5. Why it is innovative
6. Real-world impact

For every slide, provide:
- Slide title
- Main bullet points
- 1–2 short presenter speech lines
- A suggestion for what visual/diagram should appear on that slide
- Optional design idea (colors, layout, icons, graph style)

---

# Project Details

Project Name: GraphGuard AI

Tech Stack:
- TigerGraph
- FastAPI
- React
- Cytoscape or Sigma.js for graph visualization
- Optional AI risk scoring layer

Core Idea:
Traditional fraud detection systems look at individual transactions. They miss hidden links between people, devices, accounts, and phone numbers.

GraphGuard AI builds a live relationship graph and uses TigerGraph to detect hidden fraud patterns. Then an AI layer converts those graph signals into a fraud risk score.

Important positioning:
- TigerGraph is not just storage.
- TigerGraph is the decision engine.
- AI does not detect fraud alone.
- AI evaluates graph signals.

---

# Required Slide Structure

## Slide 1: Title Slide
Include:
- GraphGuard AI — Fraud Intelligence System
- Subtitle with “Detecting Hidden Fraud Networks Using Graph Intelligence”
- Name placeholder
- Tech stack badges

Visual idea:
A dark futuristic background with glowing connected nodes and one red suspicious cluster.

---

## Slide 2: Problem Statement
Explain:
- Digital fraud is growing rapidly
- Traditional systems fail to detect coordinated fraud rings
- Fraudsters reuse devices, phone numbers, and accounts

End with this line prominently:
“Current systems analyze transactions. They don’t analyze relationships.”

---

## Slide 3: Why Existing Systems Fail
Cover:
- Rule-based systems are rigid
- ML models lack relational context
- No multi-hop intelligence

Include a small example:
A → B → C → Fraud
Traditional systems miss this hidden chain.

---

## Slide 4: Our Solution
Introduce GraphGuard AI as:
- A relationship graph system
- Detects hidden connections
- Generates risk score, explanation, and fraud network visualization

---

## Slide 5: Key Innovation
Strongly emphasize:
“TigerGraph as the Decision Engine”

Mention:
- Real-time graph traversal
- Multi-hop fraud detection
- Pattern-based intelligence

This slide should make the project feel unique and technically advanced.

---

## Slide 6: System Architecture
Create a clean architecture flow:
Frontend → Backend → TigerGraph → AI Layer → Output

Explain:
- React frontend takes input
- FastAPI backend sends query
- TigerGraph finds suspicious patterns
- AI layer produces risk score
- Frontend shows results

Suggest a polished architecture diagram.

---

## Slide 7: Graph Data Model
Include nodes:
- User
- Phone
- Bank Account
- Device
- Transaction

Include edges:
- HAS_PHONE
- OWNS_ACCOUNT
- USES_DEVICE
- SENT_TO

Important line:
“This structure allows us to map real-world fraud behavior.”

---

## Slide 8: What TigerGraph Actually Does
Break this into 3 sections:
1. Multi-hop Analysis
2. Pattern Detection
3. Graph Algorithms

Examples:
- Shared device detection
- Money loops
- Fan-out scam pattern
- PageRank for influential fraud nodes
- Connected Components for fraud clusters

---

## Slide 9: Example Fraud Scenario
Build a story:
- One phone number linked to 4 accounts
- Same device reused
- Circular money transfers
- System identifies a high-risk fraud cluster

Visual should look like a red web of suspicious nodes.

---

## Slide 10: AI Risk Scoring
Explain that AI takes graph outputs and converts them into a 0–100 risk score.

Inputs:
- Suspicious connections
- Transaction loops
- Shared devices
- Fraud cluster membership

Important statement:
“AI doesn’t detect fraud alone. It evaluates graph signals.”

---

## Slide 11: API Flow
Show a simple backend API example:

POST /check-number
Input: phone number

Output:
- Risk score
- Connected accounts
- Suspicious devices
- Explanation

Provide a clean API response example.

---

## Slide 12: Frontend Experience
Show what the user sees:
- Search bar for phone/account
- Risk score meter
- Interactive graph visualization
- Explanation panel

Mention Cytoscape or Sigma.js.

---

## Slide 13: Real-World Impact
Explain how this can be used in:
- Banking fraud detection
- Fintech risk systems
- Telecom scam detection
- Anti-money laundering

End with:
“This system moves fraud detection from reactive to proactive.”

---

## Slide 14: Future Work / Demo
Mention:
- Real-time transaction streams
- LLM-generated explanations
- Payment gateway integration
- Live fraud dashboard

End the final slide with a bold closing sentence:
“GraphGuard AI turns invisible fraud relationships into visible intelligence.”

---

Additional Instructions:
- Make the content concise enough for a PPT, not long paragraphs.
- Use powerful wording and memorable one-line statements.
- Suggest modern color themes such as dark blue, black, cyan, and red for fraud alerts.
- Whenever possible, make the presentation feel like a product from a real cybersecurity startup.
- Include optional animations/transitions if useful.
- The final output should be formatted slide-by-slide with clear headings and presenter notes.

