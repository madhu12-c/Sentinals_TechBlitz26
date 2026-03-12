from typing import TypedDict, Optional


class LeadState(TypedDict):
    # ── Core lead info (set on arrival) ──────────────────────────────
    lead_id: str                        # MongoDB ObjectId as string
    source: str                         # whatsapp / form / instagram
    name: str
    phone: str
    message: str

    # ── AI outputs (set by research + score nodes) ────────────────────
    research_summary: Optional[str]     # Claude's research output
    score: Optional[int]                # 1-10
    score_reason: Optional[str]         # Plain English reason
    suggested_message: Optional[str]    # Draft outreach message

    # ── Human decision (set after interrupt) ─────────────────────────
    rep_decision: Optional[str]         # "approve" or "reject"

    # ── Outreach tracking ─────────────────────────────────────────────
    outreach_sent: bool                 # Has first outreach been sent?
    follow_up_count: int                # How many follow-ups done

    # ── Error handling ────────────────────────────────────────────────
    error: Optional[str]                # Any error message
