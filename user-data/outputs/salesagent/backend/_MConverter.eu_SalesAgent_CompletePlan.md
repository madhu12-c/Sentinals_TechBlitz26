**SalesAgent**

Complete Build Plan & Progress Report

Team Sentinals \| TechBlitz26 \| March 2026

|                                                                                                                                         |
|-----------------------------------------------------------------------------------------------------------------------------------------|
| *\"India\'s first vernacular AI sales rep --- speaks your customer\'s language, lives on WhatsApp, and gets smarter with every deal.\"* |

**1. What We Have Built**

The entire backend agent system is complete across all 7 layers of the architecture. Here is a full status of every file built:

**Backend --- COMPLETE**

| **Task**                          | **File / Location**             | **Status** |
|-----------------------------------|---------------------------------|------------|
| LeadState TypedDict               | agent/state.py                  | **DONE**   |
| LangGraph StateGraph              | agent/graph.py                  | **DONE**   |
| Node 1 --- research_lead          | agent/nodes/research.py         | **DONE**   |
| Node 2 --- score_lead             | agent/nodes/score.py            | **DONE**   |
| Node 3 --- notify_rep + interrupt | agent/nodes/notify.py           | **DONE**   |
| Node 4 --- send_outreach          | agent/nodes/outreach.py         | **DONE**   |
| Node 5 --- archive_lead           | agent/nodes/archive.py          | **DONE**   |
| Node 6 --- follow_up              | agent/nodes/followup.py         | **DONE**   |
| Node 7 --- log_to_db              | agent/nodes/log_db.py           | **DONE**   |
| Claude API integration            | integrations/claude_client.py   | **DONE**   |
| Twilio WA + Voice                 | integrations/twilio_client.py   | **DONE**   |
| SendGrid email                    | integrations/sendgrid_client.py | **DONE**   |
| MongoDB helpers                   | db/mongo.py                     | **DONE**   |
| Webhook routes                    | routes/webhook.py               | **DONE**   |
| Leads API routes                  | routes/leads.py                 | **DONE**   |
| APScheduler follow-ups            | scheduler/jobs.py               | **DONE**   |
| FastAPI main app                  | main.py                         | **DONE**   |

**Still Pending**

| **Task**                     | **File / Location**               | **Status**  |
|------------------------------|-----------------------------------|-------------|
| React Dashboard page         | frontend/src/pages/Dashboard.jsx  | **PENDING** |
| React LeadDetail page        | frontend/src/pages/LeadDetail.jsx | **PENDING** |
| Vernacular AI (Hindi etc)    | integrations/claude_client.py     | **PENDING** |
| Self-learning scoring        | agent/nodes/score.py + db         | **PENDING** |
| Onboarding form              | frontend/src/pages/Onboard.jsx    | **PENDING** |
| Instagram ads webhook        | routes/webhook.py                 | **PENDING** |
| Re-notify rep at key moments | scheduler/jobs.py                 | **PARTIAL** |
| ngrok + end-to-end test      | local setup                       | **PENDING** |

**2. Phased Build Plan for Antigravity**

Each phase is a self-contained unit of work that Antigravity can execute independently. Phases are ordered by priority --- complete Phase 1 before starting Phase 2.

<table>
<colgroup>
<col style="width: 72%" />
<col style="width: 27%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PHASE 1</strong></p>
<p><strong>React Frontend — Dashboard &amp; Lead Detail</strong></p></td>
<td><strong>HIGH PRIORITY</strong></td>
</tr>
</tbody>
</table>

Build the complete React + Vite + Tailwind frontend. Two pages only for MVP.

**Page 1 --- Dashboard (/)**

- 4 metric cards at top: Total Leads, Awaiting Approval, Approved Today, Converted

- Lead table with columns: Name, Source, Score (coloured pill), Status (badge), Time

- Agent activity log below the table (chronological list of automated actions)

- Filter dropdown by source: All / WhatsApp / Form / Instagram

- Each row clickable --- navigates to /lead/:id

**Page 2 --- Lead Detail (/lead/:id)**

- Lead avatar + name + score badge (colour coded: green 8-10, amber 5-7, red 1-4)

- Info card: phone, message, source, time received

- AI Research card: research_summary from Claude

- AI Score card: score + score_reason from Claude

- Suggested Message card: suggested_message with copy button

- Two big buttons: APPROVE (green) and REJECT (red)

- Approve/Reject calls POST /leads/:id/decide and shows success toast

**Tech Stack for Frontend**

- React + Vite + Tailwind CSS

- Recharts for the metric cards and charts

- Axios for API calls to FastAPI backend at localhost:8000

- React Router for / and /lead/:id routes

- Glassmorphism card style --- dark background, frosted glass cards

| **Task**                      | **File / Location**            | **Status**  |
|-------------------------------|--------------------------------|-------------|
| Vite + React + Tailwind setup | frontend/                      | **PENDING** |
| Dashboard.jsx                 | src/pages/Dashboard.jsx        | **PENDING** |
| LeadDetail.jsx                | src/pages/LeadDetail.jsx       | **PENDING** |
| MetricCard component          | src/components/MetricCard.jsx  | **PENDING** |
| LeadTable component           | src/components/LeadTable.jsx   | **PENDING** |
| ActivityLog component         | src/components/ActivityLog.jsx | **PENDING** |
| StatusBadge + ScorePill       | src/components/                | **PENDING** |
| API layer                     | src/api/leads.js               | **PENDING** |

<table>
<colgroup>
<col style="width: 72%" />
<col style="width: 27%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PHASE 2</strong></p>
<p><strong>Vernacular AI — Hindi &amp; Indian Language Support</strong></p></td>
<td><strong>HIGH PRIORITY</strong></td>
</tr>
</tbody>
</table>

This is the unique differentiator. The agent detects what language the lead wrote in and responds in the same language. Claude supports Hindi, Marathi, Tamil, Gujarati, Bengali natively.

**What changes in claude_client.py**

- Add language detection: read the lead\'s message and detect language using Claude

- Pass detected language to all prompts: \'Respond in Hindi. Use simple, friendly language.\'

- research_lead_prompt() --- summary written in detected language

- score_lead_prompt() --- score_reason and suggested_message in detected language

- Rep notification on WhatsApp also sent in that language

**New function to add**

detect_language(message: str) -\> str

- Calls Claude with: \'What language is this message written in? Reply with just the language name in English.\'

- Returns: Hindi / Marathi / Tamil / English / etc

- Store detected language in LeadState and MongoDB

**Onboarding form --- Company profile**

- Business name, product/service description, target audience, preferred language

- Stored in MongoDB companies collection

- Used to personalise Claude prompts: \'This business sells motorcycles to young men aged 18-30 in Maharashtra\'

| **Task**                            | **File / Location**            | **Status**  |
|-------------------------------------|--------------------------------|-------------|
| detect_language() function          | integrations/claude_client.py  | **PENDING** |
| Add language to LeadState           | agent/state.py                 | **PENDING** |
| Update all prompts for vernacular   | integrations/claude_client.py  | **PENDING** |
| Company onboarding form             | frontend/src/pages/Onboard.jsx | **PENDING** |
| Companies MongoDB collection        | db/mongo.py                    | **PENDING** |
| Inject company context into prompts | integrations/claude_client.py  | **PENDING** |

<table>
<colgroup>
<col style="width: 72%" />
<col style="width: 27%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PHASE 3</strong></p>
<p><strong>Self-Learning Scoring — AI That Gets Smarter</strong></p></td>
<td><strong>MEDIUM PRIORITY</strong></td>
</tr>
</tbody>
</table>

Every time a lead converts or goes cold, the agent analyses what the original score was vs what happened. Over time it builds a pattern and adjusts future scores. This is the moat.

**How it works**

- When rep marks a lead as Converted --- log: score was X, outcome = won

- When lead goes cold after 3 follow-ups --- log: score was X, outcome = lost

- Every 10 outcomes, Claude reads the last 50 won/lost records and writes scoring tips

- Those tips are stored as company_insights in MongoDB

- Future scoring prompts include: \'Based on past data: high-score leads from WhatsApp convert 3x better than form leads for this business\'

**New files needed**

- agent/nodes/learn.py --- reads outcomes and generates insights using Claude

- db/insights.py --- save and fetch company_insights collection

- scheduler/jobs.py --- add weekly learn job alongside follow-up jobs

**New API routes needed**

- POST /leads/:id/convert --- already built, just needs to trigger learning

- GET /insights --- returns current scoring insights for dashboard

| **Task**                          | **File / Location**              | **Status**  |
|-----------------------------------|----------------------------------|-------------|
| Outcome logging on convert/cold   | routes/leads.py                  | **PENDING** |
| learn.py node                     | agent/nodes/learn.py             | **PENDING** |
| company_insights collection       | db/mongo.py                      | **PENDING** |
| Weekly learn scheduler job        | scheduler/jobs.py                | **PENDING** |
| Inject insights into score prompt | integrations/claude_client.py    | **PENDING** |
| Insights card on Dashboard        | frontend/src/pages/Dashboard.jsx | **PENDING** |

<table>
<colgroup>
<col style="width: 72%" />
<col style="width: 27%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PHASE 4</strong></p>
<p><strong>Integration Testing + Demo Prep</strong></p></td>
<td><strong>HIGH PRIORITY</strong></td>
</tr>
</tbody>
</table>

This phase is non-negotiable before the hackathon demo. The full flow must work live end-to-end in under 60 seconds.

**Setup steps**

- Install ngrok and run: ngrok http 8000

- Paste ngrok URL into Twilio sandbox webhook settings

- Create .env from .env.example and fill all keys

- pip install -r requirements.txt

- uvicorn main:app \--reload \--port 8000

- cd frontend && npm install && npm run dev

**Demo script --- 3 test leads**

- Lead 1: High score (8-10) --- WhatsApp message showing clear purchase intent in Hindi

- Lead 2: Medium score (5-7) --- English form submission, curious but unclear

- Lead 3: Low score (1-4) --- Reject this one live to show the reject flow

**What judges must see in demo**

- Lead comes in on WhatsApp → rep gets WhatsApp notification in 10 seconds

- Rep replies APPROVE on WhatsApp → lead gets email + WhatsApp outreach instantly

- Dashboard shows real-time updates --- lead moves from Awaiting to Contacted

- LeadDetail page shows AI research, score with reason, suggested message

- Activity log shows every step the agent took

| **Task**                    | **File / Location**        | **Status**  |
|-----------------------------|----------------------------|-------------|
| ngrok setup + Twilio config | local setup                | **PENDING** |
| 3 test leads prepared       | demo script                | **PENDING** |
| Full flow end-to-end test   | all files                  | **PENDING** |
| Reset button for demo       | frontend + routes/leads.py | **PENDING** |
| Backup screenshots ready    | demo prep                  | **PENDING** |

**3. Recommended Build Order for Antigravity**

Give Antigravity one phase at a time. Do not start Phase 2 until Phase 1 is working.

|           |           |                                                         |                   |
|-----------|-----------|---------------------------------------------------------|-------------------|
| **Order** | **Phase** | **What to build**                                       | **Time estimate** |
| 1st       | Phase 1   | React frontend --- Dashboard + LeadDetail               | 3-4 hours         |
| 2nd       | Phase 4   | ngrok + integration test (do this right after frontend) | 1 hour            |
| 3rd       | Phase 2   | Vernacular AI + onboarding form + company context       | 2-3 hours         |
| 4th       | Phase 3   | Self-learning scoring --- learn.py + insights           | 2 hours           |
| 5th       | Phase 4   | Demo prep --- 3 leads, reset button, screenshots        | 1 hour            |

**4. Pitch Summary for Judges**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>One liner</strong></p>
<p><em>"SalesAgent is India's first vernacular AI sales rep. Any small business plugs in their WhatsApp — and the agent captures every lead, scores it with AI, notifies the rep, sends personalised outreach in the customer's own language, follows up automatically, and gets smarter after every deal."</em></p></td>
</tr>
</tbody>
</table>

**Why it\'s unique (say this to judges)**

- Every competitor is English-only and built for Western SaaS --- we are built for India

- WhatsApp-first means zero learning curve for Indian SMB owners

- Self-learning scoring means the product gets better the more you use it --- that\'s a real moat

- Covers the full loop: generate → capture → score → notify → outreach → follow-up → learn

**Tech stack (say this confidently)**

- LangGraph for agentic AI with human-in-the-loop interrupt

- Claude API (Anthropic) for research, scoring, vernacular message writing

- FastAPI + MongoDB backend

- Twilio for WhatsApp + Voice, SendGrid for Email

- APScheduler for automated follow-ups

- React + Vite + Tailwind for the dashboard

*SalesAgent \| Team Sentinals \| TechBlitz26 \| March 2026*
