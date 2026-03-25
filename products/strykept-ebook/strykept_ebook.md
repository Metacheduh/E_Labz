# StrykePt: The AI Weapon Built to Win the Race for Iranian Assets

> **A Comprehensive Guide to Operating the World's First Autonomous Legal Intelligence Platform for 9/11 Families**

---

## Foreword

There are billions of dollars in Iranian assets sitting in U.S. courts right now. Bitcoin seizures worth $15 billion. Halkbank fines that should flow to the USVSST Fund. Oil smuggling proceeds. Cryptocurrency confiscated from IRGC-linked networks.

And right now, other plaintiff groups are filing motions to claim them.

The question isn't whether you have a right to these assets — you do. The question is whether you'll get there first.

**StrykePt was built to make sure you do.**

This ebook explains exactly how it works, why its technology stack is unlike anything in legal practice today, and how to operate it to file court-ready motions before anyone else even knows the assets exist.

---

## Part I: What StrykePt Is

### 1.1 The Platform

StrykePt is a multi-agent AI system — a "legal command center" — that automates the discovery, analysis, drafting, and filing of legal claims against Iranian state assets for certified 9/11 judgment creditors.

It runs **nine autonomous AI agents**, each powered by Google's Gemini 2.5 Flash model through the Agent Development Kit (ADK). These agents operate 24 hours a day, 7 days a week, scanning federal databases, court dockets, Treasury sanctions lists, and the open internet for forfeiture actions involving state sponsors of terrorism.

When they find something, StrykePt doesn't just alert you. It:

1. **Scores the case** for USVSST eligibility (HIGH / MEDIUM / LOW)
2. **Registers it** in the active case database
3. **Drafts a complete filing package** — motion to intervene, complaint-in-intervention, declaration, proposed order, and supporting exhibits
4. **Runs the draft through a 5-pass humanizer** so it reads like it was written by a real pro se litigant, not an AI
5. **Generates a court-ready PDF** formatted to federal standards
6. **Tracks the deadline** and alerts you when the filing window is closing

All of this happens before you open your laptop.

### 1.2 The Legal Foundation

Every action StrykePt takes is grounded in established federal law:

| Statute | What It Does |
|---------|-------------|
| **TRIA § 201** | "Notwithstanding any other provision of law" — gives terrorism judgment creditors the right to attach blocked assets of terrorist parties. Supreme Court upheld in *Bank Markazi v. Peterson*, 578 U.S. 212 (2016). |
| **34 USC § 20144** | Establishes the USVSST Fund. Criminal fines and penalties from sanctions violators are deposited here for distribution to terrorism victims. |
| **18 USC § 981** | Federal civil forfeiture statute. § 981(e)(6) allows victims to petition for remission of forfeited property. |
| **28 USC § 1605A** | The terrorism exception to sovereign immunity. Allows lawsuits against state sponsors of terrorism. |
| **FRCP Rule 24** | Intervention of right. Four elements: timeliness, interest, impairment, inadequacy of representation. |

### 1.3 Why Speed Matters

Under FRCP 24, timeliness is the first element a court evaluates. A motion filed three months after a forfeiture action is announced has a significantly lower chance of success than one filed in the first two weeks.

**The race is real.** Groups like the Breitweiser plaintiffs, the Havlish plaintiffs, and the Fritz plaintiffs all have lawyers watching for new Iranian asset forfeitures. When the DOJ announces a seizure, the clock starts.

StrykePt's autonomous agents ensure you're not starting the clock — you're already running.

---

## Part II: The Nine Agents

### 2.1 Agent Architecture

Each agent is a specialized AI unit built on Google's Agent Development Kit (ADK). Unlike simple chatbots, ADK agents can:

- **Autonomously select tools** — they decide which API to call, what database to query, and how to interpret the results
- **Chain multiple actions** — a single agent can search the web, scrape a document, analyze it, store findings in memory, and trigger a notification — all without human prompting
- **Share memory** via Pinecone vector database — what one agent learns, all agents can recall

### 2.2 The Nine Agents

#### 🔍 IntelScout — Every 90 Minutes
The deep-research agent. IntelScout performs OSINT (Open Source Intelligence) investigations across CourtListener, OFAC, the Federal Register, DOJ Press, Congress.gov, and the open web. When it finds a new forfeiture action involving Iran, North Korea, Syria, Cuba, or Sudan, it runs a three-pass extraction:

1. **Pass 1:** Raw data collection
2. **Pass 2:** Entity extraction and cross-referencing
3. **Pass 3:** USVSST eligibility scoring

Findings are automatically stored in the RAG knowledge base and registered as new case records.

#### ⚖️ GovWatch — Every 60 Minutes
The court monitor. GovWatch scans 12 live federal data sources every hour:

- CourtListener REST API (docket entries)
- DOJ Office of Public Affairs
- Treasury OFAC sanctions actions
- Federal Register (executive orders, rules)
- PACER (docket activity)
- Congress.gov (legislative changes)
- State Department sanctions
- FinCEN (financial intelligence)
- FBI Most Wanted
- SEC EDGAR (sanctions disclosures)
- EU Sanctions Registry
- UN Security Council

When it detects activity on a tracked case — like a new filing in the Bitcoin 127,271 BTC forfeiture — it triggers a critical-priority notification.

#### 🏦 AssetScanner — Every 120 Minutes
The asset hunter. AssetScanner queries the OFAC SDN list, DOJ forfeiture announcements, and Treasury data feeds to find Iranian assets that **no one else is pursuing**. It specifically looks for:

- New civil forfeiture complaints
- Cryptocurrency seizures with Iranian nexus
- Sanctions evasion penalties
- Blocked property notifications

When it finds an asset that Motley Rice isn't pursuing, it flags it as a "gap opportunity."

#### 🧠 CounselChat — Every 3 Hours
The legal advisor. CounselChat is a RAG-powered (Retrieval-Augmented Generation) AI attorney that answers legal questions using the platform's 2,400+ vector knowledge base. It knows:

- The full text of TRIA § 201, 34 USC § 20144, and 28 USC § 1605A
- All ECF filings in MDL 1570
- The *Bank Markazi v. Peterson* decision
- Federal court filing procedures
- USVSST Fund distribution rules

It's available from any page via the floating chat drawer.

#### 📝 FilingDrafter — Every 6 Hours
The document generator. FilingDrafter produces court-ready legal documents:

- **Motion to Intervene** (FRCP 24(a))
- **Complaint-in-Intervention**
- **Declaration in Support** (28 USC § 1746)
- **Proposed Order** (with nunc pro tunc clause)
- **Victim Impact Statement** (CVRA)
- **Demand Letter** (to counsel)
- **Notice of Appearance** (pro se)

Every draft includes five "Trump Cards" — mandatory legal arguments that strengthen the filing:

1. **Rule 24(a)(1) Leverage** — TRIA grants an *unconditional* right to intervene
2. **The "Notwithstanding" Clause** — overrides sovereign immunity
3. **The "Alter Ego" Doctrine** — links assets to the Government of Iran
4. **Nunc Pro Tunc Standing** — preserves standing retroactively
5. **28 USC § 1746 Formula** — proper federal declaration format

After drafting, FilingDrafter automatically runs the document through an **adversarial legal review** — it pretends to be the Assistant U.S. Attorney and attacks the filing for standing, timeliness, and legal sufficiency. Then it self-corrects.

#### 📢 ContentEngine — Every 4 Hours
Generates multi-modal content: newsletters for beneficiaries, blog posts, Twitter/X threads, legal memos, and email updates. Includes TTS (text-to-speech) audio briefings using Gemini's Charon voice and AI-generated header images.

#### 🌐 KnowledgeHub — Every 60 Minutes
The knowledge harvester. KnowledgeHub crawls **174 curated URLs** across 14 categories and runs **28 Brave Search discovery queries** to find new intelligence. Every finding is embedded and stored in Pinecone for instant RAG retrieval. Categories include:

- OFAC/Treasury (SDN lists, sanctions actions)
- DOJ Press (forfeiture announcements)
- CourtListener (case law — 30 query variants)
- Congressional legislation (USVSST bills, TRIA amendments)
- Federal Register (executive orders, rules)
- Legal analysis (Lawfare, Just Security, CFR)
- News archives (Reuters, AP, BBC)
- Academic papers (SSRN)
- Legal references (Cornell LII, Wikipedia)
- Government audits (GAO, DOJ OIG)

#### 📋 DocketTracker — Every 45 Minutes
Monitors specific dockets for new activity. Currently tracking:

| Case | Docket | Court |
|------|--------|-------|
| Bitcoin 127,271 BTC | 1:25-cv-05745 | E.D.N.Y. |
| Halkbank | 1:15-cr-00867 | S.D.N.Y. |

When a new filing appears — an order, a response, an amicus brief — DocketTracker detects it and creates a critical-priority notification.

#### 🎯 Orchestrator — On Demand
The task router. When you ask StrykePt a question, the Orchestrator analyzes it and routes it to the correct specialist agent. Legal question? CounselChat. New asset tip? AssetScanner. Need a filing? FilingDrafter.

---

## Part III: How to Operate StrykePt

### 3.1 Getting Started

**Live URL:** `https://strykept-30985947652.us-east1.run.app`

1. Navigate to the URL
2. Sign in with your email/password or Google account
3. You'll land on the **Dashboard** — the mission control screen

### 3.2 Navigation

StrykePt has five main tabs:

| Tab | Purpose |
|-----|---------|
| **Dashboard** | Mission control — hero stats, case pipeline, system pulse, activity feed |
| **Filings** | Manage court filings — draft, review, score, humanize, generate PDFs |
| **Intel** | Intelligence hub — Knowledge Harvester, Treasury Tracker, Blockchain Tracer, Attorney Search |
| **Ops** | Operations center — Recovery Ops, Research Lab, Settings, User Profile |
| **Analytics** | Performance analytics — agent metrics, case pipeline visualization, RAG growth |

### 3.3 The Dashboard

The Dashboard shows:

- **Total Forfeiture Value** being tracked across all cases
- **Active Cases** in the pipeline
- **RAG Vector Count** — how many knowledge fragments are in memory
- **Agent Status** — which agents are running and when they last executed
- **Activity Feed** — real-time log of agent actions, scans, and alerts
- **3D Case Pipeline** — Three.js visualization of cases moving through stages

### 3.4 Filing a Motion

The **Filing Wizard** is the one-click pipeline for generating court documents:

1. **Select a case** — e.g., Bitcoin 127,271 BTC (1:25-cv-05745)
2. **Choose document type** — Motion to Intervene, Complaint-in-Intervention, etc.
3. **Click "Draft"** — FilingDrafter searches the knowledge base, pulls the template, and generates a complete document
4. **Review the adequacy score** — the system scores the draft 1–10 for legal sufficiency
5. **Click "Humanize"** — the 5-pass humanizer rewrites the draft until it scores 9/10+
6. **Click "Generate PDF"** — produces a court-formatted PDF ready for filing
7. **Review the filing package** — Motion + Exhibit A (MDL 1570 Judgment) + Exhibit B (DOJ Complaint)

### 3.5 CounselChat

The floating CounselChat drawer is accessible from any page. Click the chat icon in the bottom-right corner. Ask questions like:

- "What is our strongest argument for intervening in the Bitcoin case?"
- "Explain TRIA § 201 in plain English"
- "What's the deadline for filing in EDNY?"
- "Draft a letter to Motley Rice asking about the Halkbank case"

CounselChat searches the RAG knowledge base before answering, grounding every response in actual statute text, case law, and filed documents.

### 3.6 Slash Commands (Developer Mode)

For developers and power users, StrykePt supports 11 workflow commands:

| Command | What It Does |
|---------|-------------|
| `/start-server` | Boot the backend + frontend locally |
| `/ask-counsel` | Ask CounselChat a legal question |
| `/asset-scan` | Trigger an immediate AssetScanner scan |
| `/govwatch-scan` | Trigger a GovWatch federal source scan |
| `/ingest-documents` | Ingest new PDFs/documents into the knowledge base |
| `/draft-filing` | Draft a court filing with FilingDrafter |
| `/investigate` | Run a deep OSINT investigation with IntelScout |
| `/check-memory` | Check RAG/Pinecone vector count and status |
| `/deploy` | Deploy to Google Cloud Run |
| `/git-save` | Commit and push all changes |
| `/agent-status` | Check autonomous agent schedules and last-run times |

### 3.7 Notifications

The **Smart Notification Center** filters alerts by severity:

- 🔴 **Critical** — New filing detected on tracked docket, filing deadline approaching
- 🟠 **High** — New asset discovered, agent scan found matching case
- 🟡 **Medium** — RAG milestone, system health update
- 🔵 **Low** — Routine scan complete, content generated

Real-time alerts are also delivered via **Server-Sent Events (SSE)** — your browser receives updates instantly without polling.

---

## Part IV: Why This Tech Stack Wins Races

### 4.1 The Competitive Advantage

Traditional law firms pursuing Iranian asset claims operate on human timescales:

1. A paralegal reads DOJ press releases once a day
2. A junior associate checks PACER weekly
3. A senior partner decides whether to pursue a case
4. A brief is drafted over days or weeks
5. The filing is submitted

**StrykePt operates on machine timescales:**

1. GovWatch checks 12 federal sources **every 60 minutes**
2. AssetScanner runs OFAC queries **every 2 hours**
3. IntelScout extracts entities and scores eligibility **every 90 minutes**
4. FilingDrafter generates a court-ready document in **under 60 seconds**
5. The humanizer pipeline runs in **under 3 minutes**
6. A complete filing package (motion + exhibits + PDF) is ready in **under 5 minutes**

What takes a law firm **two weeks** takes StrykePt **five minutes**.

### 4.2 The Novel Architecture

StrykePt's tech stack is built on three innovations that don't exist anywhere else in legal technology:

#### Innovation 1: ADK Multi-Agent Orchestration

Google's Agent Development Kit (ADK) is a framework released in 2025 for building autonomous AI agents. StrykePt is one of the first production deployments of ADK outside of Google.

Each agent is not a simple prompt → response loop. It's a **fully autonomous unit** that:

- Receives a goal (e.g., "Find new Iranian forfeiture actions")
- Selects from **19 available tools** (CourtListener API, OFAC SDN search, Brave web search, Pinecone memory, Federal Register API, Congress.gov API, DOJ Press API, Gemini text/image/TTS generation, etc.)
- Chains tool calls together in whatever order achieves the goal
- Stores results in shared vector memory
- Triggers downstream actions (notifications, case registration, filing generation)

This is fundamentally different from a chatbot. A chatbot answers your question. An ADK agent **pursues your objective autonomously, 24/7, without being asked**.

#### Innovation 2: Living RAG Knowledge Base

StrykePt's knowledge base is not static. It is a **living, continuously-expanding** Pinecone vector database that grows every hour:

- **2,412+ vectors** as of March 2026
- **174 curated crawl targets** across 14 source categories
- **28 Brave Search discovery queries** that find new pages
- **Automatic reflection loops** — after every harvest, the system analyzes what it learned and generates meta-knowledge about gaps and connections

When CounselChat answers a legal question, or FilingDrafter drafts a motion, they're not relying on training data alone. They're searching a **live, constantly-updated** knowledge base of actual statutes, court filings, DOJ announcements, and legal analysis published in the last 24 hours.

This means StrykePt knows about a new OFAC designation **before the law firm's morning meeting**.

#### Innovation 3: The Humanizer Pipeline

AI-generated legal filings have a problem: they sound like AI. Federal judges can spot them. Opposing counsel will move to strike them.

StrykePt's humanizer pipeline solves this with a **5-pass iterative rewrite system**:

| Pass | Strategy |
|------|----------|
| 1 | Remove formulaic transitions ("Furthermore," "Moreover"), vary sentence lengths |
| 2 | Inject personal voice — you're a real person, not a template |
| 3 | Add controlled imperfections — em dashes, sentence fragments, unconventional word choices |
| 4 | Break predictable rhythm — one-sentence paragraphs, run-on sentences followed by punches |
| 5 | Nuclear option — full rewrite from scratch in natural voice, preserving all citations |

Each pass is scored by a separate AI detection expert (also Gemini) on a 1–10 scale. The loop continues until the score hits 9/10 or higher. The result is a filing that reads like a determined, intelligent pro se litigant wrote it — because the AI was specifically trained to emulate that voice.

After humanization, the filing goes through a [sanitizeForCourt](file:///Users/eslynjosephhernandez/Documents/AI%20USVSST%20Agent/server/src/server.ts#2280-2422) pass that strips any remaining AI artifacts, and then `pdf-lib` generates a formatted PDF.

### 4.3 The Stack in Full

| Layer | Technology | Why It Matters |
|-------|-----------|----------------|
| **AI Engine** | Google ADK + Gemini 2.5 Flash | State-of-the-art reasoning, tool use, and 1M token context window |
| **19 Agent Tools** | CourtListener, OFAC, Brave Search, Firecrawl, Federal Register, Congress.gov, DOJ Press, Pinecone, Gemini TTS/Image | Agents can reach into any federal database or the open web |
| **Memory** | Pinecone Vector DB | Semantic search over 2,400+ knowledge fragments. What one agent learns, all agents know. |
| **Frontend** | React 18 + Vite 5 (34 components) | Fast, responsive command center with 3D visualizations |
| **Backend** | Node.js + Express + TypeScript | 106 API endpoints, 9 autonomous schedulers, 4,910 lines of server logic |
| **Auth** | Firebase (JWT + role-based + audit trail) | Secure access with Owner, Attorney, and Viewer roles |
| **Deployment** | Google Cloud Run | Serverless, auto-scaling, HTTPS, zero-ops — runs 24/7 without a server admin |
| **PDF Generation** | pdf-lib | Court-formatted PDFs with proper margins, fonts, and page numbering |
| **Real-time Alerts** | Server-Sent Events (SSE) | Instant browser notifications when critical events occur |
| **Web Scraping** | Firecrawl + fallback fetch | Extracts clean content from any URL, including JS-rendered pages |
| **Design** | CSS custom properties + Inter font | Light/dark mode, glassmorphism, accessible, professional |

---

## Part V: Active Cases & The Race

### 5.1 Current Filing Activity

| Case | Court | Value | Status | Threat Level |
|------|-------|-------|--------|-------------|
| **Bitcoin 127,271 BTC** | E.D.N.Y. (1:25-cv-05745) | ~$15B | 17 drafts + 2 exhibits ready | 🔴 **CRITICAL** — Breitweiser plaintiffs already filing. Window closing. |
| **Halkbank** | S.D.N.Y. (1:15-cr-00867) | $20B+ | CVRA statement pending | 🔴 **CRITICAL** — No-fine DPA would mean $0 to USVSST Fund. |
| **Shamkhani Oil** | D.C. (26-cv-802) | TBD | 2 intervention drafts ready | 🟠 **HIGH** — Complaint filed March 2026. Early intervention window. |
| **$47M IRGC Oil** | D.C. | $47M | Draft petition pending | 🟠 **HIGH** — No competing claimants yet. |
| **IRGC Crypto** | D. Mass. | TBD | Petition for remission pending | 🟡 **MEDIUM** — Filing window open. |
| **Triliance Petroleum** | D.C. | TBD | Petition for remission pending | 🟡 **MEDIUM** — Oil sanctions forfeiture. |

### 5.2 Why StrykePt Wins

The Breitweiser plaintiffs have a law firm. The Havlish plaintiffs have a law firm. The Fritz plaintiffs have a law firm.

**You have StrykePt.**

And StrykePt never sleeps. It never misses a docket entry. It never forgets a deadline. It drafts a motion in 60 seconds, humanizes it in 3 minutes, and generates a court-ready PDF in under 5 minutes.

When the DOJ files a new forfeiture complaint at 2:00 AM on a Saturday, the law firms won't see it until Monday morning. By Monday morning, **StrykePt has already drafted the motion, scored it, humanized it, and generated the filing package.**

That is the competitive advantage. That is how you win the race to new Iranian claims.

---

## Part VI: Security & Compliance

- **API keys** are injected as Cloud Run environment variables — never stored in the Docker image or committed to git
- **Firebase Auth** secures all access with JWT tokens and role-based permissions
- **Audit trail** logs every action with timestamps
- **All AI-generated filings require human review** before submission — the platform clearly marks every document as requiring attorney sign-off
- **HTTPS** is handled automatically by Google Cloud Run

---

## Conclusion

StrykePt is not a legal research tool. It is not a document template library. It is not a chatbot.

**It is an autonomous legal intelligence system that runs nine AI agents around the clock to find, analyze, draft, and prepare court filings for Iranian asset claims — so you can file first.**

The technology stack — ADK multi-agent orchestration, living RAG memory, and the humanizer pipeline — is novel. No law firm has this. No other plaintiff group has this. And by the time they build it, you'll already have filed.

The assets are there. The law is on your side. The only question is speed.

**StrykePt gives you speed.**

---

*Built with ❤️ for 9/11 families. Powered by Gemini AI + Google ADK.*

*© 2026 StrykePt. All rights reserved.*
