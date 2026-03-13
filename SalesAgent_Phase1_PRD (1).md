# SalesAgent — Phase 1 React Frontend
### PRD + Technical Specification for Antigravity
**Team Sentinals | TechBlitz26 | March 2026**

---

> ⚠️ **IMPORTANT — Read before building**
> The backend is **100% complete**. Do NOT modify any backend files.
> Your job is to build only the React frontend that calls the existing FastAPI backend at `http://localhost:8000`.
> Every API endpoint is documented in Section 4.

| Backend status | Your job | Pages to build | Backend URL |
|---|---|---|---|
| ✅ COMPLETE | Frontend only | 2 pages | `localhost:8000` |

---

## SECTION 1 — Project Overview

### What is SalesAgent?

SalesAgent is an AI-powered sales lead automation platform for small and mid-size Indian businesses. When a potential customer (lead) sends a WhatsApp message or fills a website form, the backend AI agent automatically researches the lead, scores them 1–10, notifies the sales rep on WhatsApp, and sends outreach messages. Everything is automated.

### What the backend already does — DO NOT TOUCH

- Receives leads from WhatsApp and website forms via webhook
- Calls Claude AI to research who the lead is and what they want
- Scores the lead 1–10 with a written reason
- Drafts a personalised outreach message in the lead's language
- Sends a WhatsApp notification to the sales rep with the score
- Pauses and waits for the rep to approve or reject (LangGraph `interrupt()`)
- If approved: sends email + WhatsApp + voice call to the lead
- If rejected: archives the lead in MongoDB
- Automatically follows up 3 times if no reply
- Logs every agent action to MongoDB `agent_events` collection

### What you are building — Phase 1

A React web dashboard. **Two pages only.**

| Page | Route | Purpose |
|---|---|---|
| Dashboard | `/` | All leads, KPI metrics, agent activity log |
| Lead Detail | `/lead/:id` | Full AI analysis for one lead + approve/reject buttons |

---

## SECTION 2 — Tech Stack and Project Setup

### Frontend tech stack — use exactly these

| Library | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| Vite | 5 | Build tool (fast) |
| Tailwind CSS | 3 | Styling |
| React Router | 6 | Page routing (`/` and `/lead/:id`) |
| Axios | 1.x | HTTP calls to FastAPI backend |
| Recharts | 2.x | Metric charts and score visualisation |
| React Hot Toast | 2.x | Toast notifications for approve/reject |
| Lucide React | latest | Icons throughout the UI |

### Setup commands — run these in order

```bash
cd salesagent
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-router-dom axios recharts react-hot-toast lucide-react

# Start dev server
npm run dev
# Frontend runs on http://localhost:5173
# Backend must already be running on http://localhost:8000
```

### Folder structure to create

```
frontend/src/
  api/
    leads.js              <- All axios calls to backend (copy from Section 5)
  components/
    MetricCard.jsx        <- KPI card (number + label + icon)
    LeadTable.jsx         <- Table of all leads with filter
    ActivityLog.jsx       <- Chronological agent event list
    StatusBadge.jsx       <- Coloured status pill
    ScorePill.jsx         <- Score badge (1-10, colour coded)
    LoadingSpinner.jsx    <- Simple spinner
  pages/
    Dashboard.jsx         <- Page 1
    LeadDetail.jsx        <- Page 2
  App.jsx                 <- Router setup (copy from Section 8)
  main.jsx
  index.css               <- Tailwind directives + global styles
```

### tailwind.config.js — paste this exactly

```js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          teal:  '#0F6E56',
          light: '#E1F5EE',
          dark:  '#085041',
        }
      }
    }
  },
  plugins: [],
}
```

### index.css — paste this exactly

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #0d1117;
  color: #e6edf3;
  font-family: 'Inter', system-ui, sans-serif;
}

.glass-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(12px);
  border-radius: 12px;
}
```

---

## SECTION 3 — Page-by-Page UI Specification

### Page 1 — Dashboard `(route: /)`

> **Purpose:** The business owner or sales rep lands here first. See all leads at a glance, check AI agent activity, filter by source, click any lead to view detail.

#### Layout — top to bottom

1. **Top navbar** — `SalesAgent` app name left, green live dot + `Add Test Lead` button right
2. **Row of 4 metric cards** — Total Leads / Awaiting Approval / Approved / Converted
3. **Filter bar** — dropdown (All / WhatsApp / Form / Instagram) + lead count
4. **Lead table** — full width, all leads, each row clickable
5. **Agent activity log** — below the table, last 20 agent events, auto-refreshes every 10s

#### Metric cards — 4 cards in a row

| Card | Value from API | Icon | Badge colour |
|---|---|---|---|
| Total Leads | `metrics.total` | `Users` | Blue |
| Awaiting | `metrics.awaiting` | `Clock` | Amber + pulse animation |
| Approved | `metrics.approved` | `CheckCircle` | Green |
| Converted | `metrics.converted` | `Star` | Purple |

#### Lead table — columns

| Column | Field | Display | Notes |
|---|---|---|---|
| Name | `name` | Avatar + text | Initials avatar beside name |
| Source | `source` | Badge | `whatsapp`=green, `form`=blue, `instagram`=purple |
| Score | `score` | ScorePill | 1-4=red, 5-7=amber, 8-10=green, null=gray |
| Status | `status` | StatusBadge | See colour mapping below |
| Time | `created_at` | Time ago | e.g. `2 mins ago` |
| Action | — | View button | Navigates to `/lead/:id` |

#### Status badge colour mapping

| Status value | Badge colour | What it means |
|---|---|---|
| `new` | Gray | Just arrived, agent not started |
| `researching` | Blue (animated) | Agent is researching right now |
| `scored` | Blue | AI has scored the lead |
| `awaiting_decision` | Amber + pulse dot | Waiting for rep to decide |
| `contacted` | Green | Outreach sent to lead |
| `follow_up` | Green | Auto following up |
| `converted` | Purple | Lead became a customer |
| `rejected` | Red | Rep rejected this lead |
| `cold` | Gray | No reply after 3 follow-ups |

#### Data fetching on Dashboard

```js
// On page load, fetch all 3 in parallel:
const [metrics, leads, events] = await Promise.all([
  api.getMetrics(),   // GET /leads/metrics
  api.getLeads(),     // GET /leads
  api.getEvents(),    // GET /events?limit=20
])

// Auto-refresh every 10 seconds:
useEffect(() => {
  const id = setInterval(fetchAll, 10000)
  return () => clearInterval(id)
}, [])
```

---

### Page 2 — Lead Detail `(route: /lead/:id)`

> **Purpose:** Rep reviews full AI analysis for one lead. Most important page — this is where approve/reject happens.

#### Layout — top to bottom

1. **Back button** — `<- Back to Dashboard` — navigates to `/`
2. **Lead header** — avatar, name (large), ScorePill, source badge, time received
3. **2x2 grid of info cards:**
   - **Card A — Lead Info:** phone, original message, source, email (if available)
   - **Card B — AI Research:** `research_summary` from Claude (paragraph of text)
   - **Card C — AI Score:** big score number + `score_reason` + progress bar
   - **Card D — Suggested Message:** `suggested_message` with Copy button top-right
4. **Two full-width action buttons** (only if status is `awaiting_decision` or `scored`)
   - APPROVE button — green, full width, confirmation modal on click
   - REJECT button — red outlined, full width, confirmation modal on click
5. **Lead timeline** — all `agent_events` for this lead in chronological order

#### Score card (Card C) — detailed spec

- Show score as big number: `8 / 10`
- Colour rules: `1-4` = red `#A32D2D`, `5-7` = amber `#854F0B`, `8-10` = green `#0F6E56`
- Progress bar below the number: filled width = `(score / 10) * 100%`
- `score_reason` text below the bar in normal body size

#### Suggested message card (Card D) — detailed spec

- `Copy Message` button in top-right corner of card
- On click: copies to clipboard, button changes to `Copied!` for 2 seconds then reverts
- If `suggested_message` is null: show `AI is generating...` in muted gray text

#### Approve / Reject buttons — detailed spec

- **Only show** if status is `awaiting_decision` OR `scored`
- **APPROVE:** full width, large (`h-14`), green bg `#0F6E56`, white text, check icon
- **REJECT:** full width, large (`h-14`), transparent bg, red border, red text, X icon
- On click either button: show a **confirmation modal** before calling API
- APPROVE modal: *"Approve this lead? The agent will send outreach immediately."*
- REJECT modal: *"Reject this lead? It will be archived and no outreach will be sent."*
- On confirm APPROVE → `POST /leads/:id/decide` with `{ decision: 'approve' }`
- On confirm REJECT → `POST /leads/:id/decide` with `{ decision: 'reject' }`
- On success APPROVE → green toast: `"Lead approved! Outreach is being sent."`
- On success REJECT → red toast: `"Lead archived."`
- After decision: hide both buttons, show status banner with new status
- If status is `contacted` / `rejected` / `converted` / `cold` — hide buttons, show read-only banner

#### Data fetching on Lead Detail

```js
// On page load:
const lead   = await api.getLead(id)        // GET /leads/:id
const events = await api.getEvents(id, 30)  // GET /events?lead_id=:id&limit=30

// Auto-refresh lead status every 5 seconds:
useEffect(() => {
  const id = setInterval(() => fetchLead(), 5000)
  return () => clearInterval(id)
}, [])
```

---

## SECTION 4 — Backend API Reference

**Base URL:** `http://localhost:8000`

> **CORS note:** The backend already has CORS enabled for `localhost:5173`. Call `localhost:8000` directly from Axios. No proxy needed.

### All endpoints

| Method | Endpoint | What it returns |
|---|---|---|
| `GET` | `/` | Health check: `{ status: 'ok' }` |
| `GET` | `/leads/metrics` | KPI counts: total, awaiting, approved, converted |
| `GET` | `/leads` | All leads array, sorted newest first. Optional: `?limit=50` |
| `GET` | `/leads/{lead_id}` | Full detail for one lead including all AI fields |
| `POST` | `/leads/{lead_id}/decide` | Approve or reject. Body: `{ decision: 'approve' or 'reject' }` |
| `POST` | `/leads/{lead_id}/convert` | Mark lead as converted (won deal) |
| `GET` | `/events` | Activity log. Optional: `?lead_id=xxx&limit=30` |
| `POST` | `/webhook/form` | Submit test lead for demo. Body shown below. |

### Response shapes

#### `GET /leads/metrics`

```json
{
  "total":     12,
  "awaiting":  3,
  "approved":  7,
  "converted": 2
}
```

#### `GET /leads` — array of lead objects

```json
{
  "leads": [
    {
      "_id":              "64f3a1b2c3d4e5f6a7b8c9d0",
      "name":             "Rajesh Kumar",
      "phone":            "+919876543210",
      "source":           "whatsapp",
      "message":          "Hi, I want to buy a bike",
      "status":           "awaiting_decision",
      "score":            8,
      "score_reason":     "Clear purchase intent, specific question",
      "suggested_message":"Hi Rajesh! Thanks for reaching out...",
      "research_summary": "Rajesh appears to be an adult male...",
      "outreach_sent":    false,
      "follow_up_count":  0,
      "created_at":       "2026-03-12T18:30:00Z",
      "updated_at":       "2026-03-12T18:30:45Z"
    }
  ],
  "count": 1
}
```

#### `GET /leads/{lead_id}` — same shape as above but single object (not in array)

#### `POST /leads/{lead_id}/decide`

```json
// Request
{ "decision": "approve" }
// or
{ "decision": "reject" }

// Response
{ "status": "ok", "decision": "approve", "lead_id": "64f3..." }
```

#### `GET /events`

```json
{
  "events": [
    {
      "_id":         "...",
      "lead_id":     "64f3a1b2c3d4e5f6a7b8c9d0",
      "node":        "score_lead",
      "description": "Lead scored 8/10 - Clear purchase intent",
      "channel":     null,
      "timestamp":   "2026-03-12T18:30:45Z"
    }
  ]
}
```

#### `POST /webhook/form` — use this to submit test leads

```json
{
  "name":    "Rajesh Kumar",
  "phone":   "+919876543210",
  "email":   "rajesh@example.com",
  "message": "Hi, I want to buy a bike. Budget 1.5 lakh.",
  "source":  "form"
}
```

---

## SECTION 5 — API Layer `src/api/leads.js`

Create this file at `src/api/leads.js`. Import functions from here in your pages. **Never write axios calls directly inside components.**

```js
import axios from 'axios'

const BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export const getMetrics = () =>
  api.get('/leads/metrics').then(r => r.data)

export const getLeads = (limit = 50) =>
  api.get('/leads', { params: { limit } }).then(r => r.data.leads)

export const getEvents = (leadId = null, limit = 20) =>
  api.get('/events', { params: { lead_id: leadId, limit } }).then(r => r.data.events)

export const getLead = (id) =>
  api.get(`/leads/${id}`).then(r => r.data)

export const decideLead = (id, decision) =>
  api.post(`/leads/${id}/decide`, { decision }).then(r => r.data)

export const convertLead = (id) =>
  api.post(`/leads/${id}/convert`).then(r => r.data)

export const submitTestLead = (data) =>
  api.post('/webhook/form', data).then(r => r.data)
```

---

## SECTION 6 — Component Specifications

### `MetricCard.jsx`

```
Props:
  label   : string   — 'Total Leads'
  value   : number   — the count to display
  icon    : component from lucide-react
  color   : string   — 'blue' | 'amber' | 'green' | 'purple'
  loading : boolean  — show skeleton shimmer if true

Style: glass-card, 24px padding
  - Icon top-right corner, 24px, colour-matched
  - Big number centre: 32px bold white
  - Label below: 14px muted
  - Skeleton: animated pulse gray bars when loading=true
```

### `ScorePill.jsx`

```
Props:
  score: number (1-10) or null

1-4:  red bg   #FCEBEB  red text   #A32D2D
5-7:  amber bg #FAEEDA  amber text #854F0B
8-10: green bg #E1F5EE  green text #0F6E56
null: gray bg  #F1EFE8  gray text  #444441  shows '...'

Style: rounded-full, px-3 py-1, text-sm font-medium
```

### `StatusBadge.jsx`

```
Props:
  status: string

new               -> gray
researching       -> blue (animated)
scored            -> blue
awaiting_decision -> amber + pulse dot
contacted         -> green
follow_up         -> green
converted         -> purple
rejected          -> red
cold              -> gray
```

### `ActivityLog.jsx`

```
Props:
  events : array   — event objects from GET /events
  loading: boolean

Renders a vertical timeline list.
Each item: coloured dot + node name (bold) + description + time ago

Node -> dot colour:
  research_lead  -> blue
  score_lead     -> purple
  notify_rep     -> amber
  send_outreach  -> green
  follow_up      -> green
  archive_lead   -> red
  log_to_db      -> gray
  ui_decision    -> teal
  webhook        -> gray
```

---

## SECTION 7 — Design System

### Overall visual style

- **Dark background:** `#0d1117`
- **Cards:** glassmorphism — `rgba(255,255,255,0.05)` bg, `1px rgba(255,255,255,0.1)` border, `blur(12px)`
- **Primary accent:** teal `#0F6E56` — buttons, brand name, active states
- **All cards:** `border-radius: 12px`
- No pure white anywhere — use `rgba(255,255,255,0.7)` or `rgba(255,255,255,0.9)` for text

### Colour palette

| Name | Hex | Use case | Tailwind |
|---|---|---|---|
| Brand Teal | `#0F6E56` | Primary buttons, links | custom in config |
| Green | `#1D9E75` | Approved, contacted | `green-600` |
| Amber | `#BA7517` | Awaiting, medium score | `amber-700` |
| Red | `#E24B4A` | Rejected, low score | `red-500` |
| Blue | `#378ADD` | Researching, info | `blue-500` |
| Purple | `#7F77DD` | Converted, high value | `purple-500` |
| Page bg | `#0d1117` | Body background | `gray-950` |
| Card bg | `rgba(255,255,255,0.05)` | Glass card surface | custom |

### Typography

| Element | Size | Weight | Colour |
|---|---|---|---|
| App name | 24px | 700 | white |
| Section headings | 18px | 600 | `rgba(255,255,255,0.9)` |
| Card titles | 14px | 600 | `rgba(255,255,255,0.9)` |
| Body text | 14px | 400 | `rgba(255,255,255,0.7)` |
| Metric number | 32px | 700 | white |
| Score number (big) | 48px | 700 | by score colour |
| Time / small labels | 12px | 400 | `rgba(255,255,255,0.4)` |

---

## SECTION 8 — App.jsx Router Setup

Copy this exactly as your `App.jsx`:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Dashboard  from './pages/Dashboard'
import LeadDetail from './pages/LeadDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/"         element={<Dashboard />}  />
        <Route path="/lead/:id" element={<LeadDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

## SECTION 9 — Demo Test Leads and Checklist

### Add `Add Test Lead` button to Dashboard navbar

Add a button in the top-right of the Dashboard. On click, call `POST /webhook/form` with the test data below. This simulates a real lead without needing actual WhatsApp.

### Test Lead 1 — High score *(approve this live in demo)*

```json
{
  "name":    "Rajesh Kumar",
  "phone":   "+919876543210",
  "email":   "rajesh@example.com",
  "message": "Bhai mujhe ek achhi bike chahiye, 150cc ya 200cc. Budget 1.5 lakh hai.",
  "source":  "form"
}
```

> Expected score: **8–9** (clear intent, budget stated, Hindi message shows vernacular support)

### Test Lead 2 — Medium score

```json
{
  "name":    "Priya Sharma",
  "phone":   "+919123456789",
  "email":   "priya@gmail.com",
  "message": "Hi, I saw your ad. Just wanted to know what bikes you have.",
  "source":  "form"
}
```

> Expected score: **5–6** (curious but vague, no budget)

### Test Lead 3 — Low score *(reject this live in demo)*

```json
{
  "name":    "Unknown",
  "phone":   "+910000000000",
  "email":   null,
  "message": "hello",
  "source":  "whatsapp"
}
```

> Expected score: **1–3** (no intent, no info)

### Demo script — what judges must see

1. Both backend (port 8000) and frontend (port 5173) running
2. Open Dashboard — metrics all 0, table empty
3. Click **Add Test Lead**, submit Lead 1 (Rajesh, Hindi message)
4. Watch Dashboard auto-refresh — Lead 1 goes: `new` > `researching` > `scored` > `awaiting_decision`
5. Click **View** on Lead 1 — LeadDetail shows AI research, score 8+, suggested message in Hindi
6. Click **APPROVE** — confirm modal — toast `"Outreach sent!"` appears
7. Go back to Dashboard — Lead 1 status changes to `contacted` in real time
8. Activity log shows full chain: `webhook` > `research_lead` > `score_lead` > `notify_rep` > `send_outreach`
9. Submit Lead 3 (Unknown, `"hello"`) — wait for score — click **REJECT** — shows archived in red
10. Point out 3 different scores showing the AI scoring system works

---

> ⚠️ **Final reminders for Antigravity**
>
> 1. **Do NOT touch any backend files.** The backend is complete and working.
> 2. Backend must be running at `localhost:8000` before testing the frontend.
> 3. The `_id` field from MongoDB is your `lead_id` in all API calls.
> 4. Auto-refresh is critical — agent processes leads asynchronously.
> 5. If an API call fails, confirm backend is running and CORS is allowing `localhost:5173`.
> 6. Run `uvicorn main:app --reload --port 8000` from the backend folder.
> 7. Run `npm run dev` from the frontend folder.

---

*SalesAgent | Team Sentinals | TechBlitz26 | Phase 1 Frontend Spec*
