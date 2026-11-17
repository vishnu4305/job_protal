from datetime import date
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from database import get_session
from models import *

router = APIRouter(prefix="/tracker", tags=["Tracker"])
TRACKER_STATUSES = ["Wishlist", "Applied", "Interview", "Offer", "Rejected"]
PORTAL_TO_TRACKER = {
    "Applied": "Applied",
    "Shortlisted": "Interview",
    "Rejected": "Rejected",
    "Hired": "Offer",
}

class TrackRequest(BaseModel):
    candidate_id: int
    job_id: Optional[int] = None      
    company: Optional[str] = None   
    role: Optional[str] = None
    source: str = "Manual"
    status: str = "Wishlist"
    applied_date: Optional[date] = None
    notes: Optional[str] = None


class TrackUpdateRequest(BaseModel):
    candidate_id: int
    status: Optional[str] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None


# Called from main.py so the tracker stays in sync with the portal.
# It does not commit; the caller commits.
def sync_tracker(session, candidate_id, job_id, portal_status):
    status = PORTAL_TO_TRACKER.get(portal_status)
    if status is None:
        return
    tracked = session.query(TrackedJob).filter(
        TrackedJob.candidate_id == candidate_id,
        TrackedJob.job_id == job_id
    ).first()
    if tracked:
        tracked.status = status
        if tracked.applied_date is None:
            tracked.applied_date = date.today()
        return
    job = session.query(Job.title, Employee.company_name).join(
        Employee, Job.employee_id == Employee.employee_id
    ).filter(Job.job_id == job_id).first()
    if job is None:
        return

    session.add(TrackedJob(
        candidate_id=candidate_id,
        job_id=job_id,
        company=job.company_name,
        role=job.title,
        source="Portal",
        status=status,
        applied_date=date.today()
    ))

# ADD A JOB TO THE TRACKER
@router.post("/add")
def add_tracked_job(req: TrackRequest):
    if req.status not in TRACKER_STATUSES:
        return {"message": f"Invalid status. Use: {', '.join(TRACKER_STATUSES)}"}
    session = get_session()
    candidate = session.query(Candidate).filter(
        Candidate.candidate_id == req.candidate_id
    ).first()
    if not candidate:
        session.close()
        return {"message": "Candidate not found"}
    company = (req.company or "").strip()
    role = (req.role or "").strip()
    source = req.source.strip() or "Manual"
    status = req.status
    if req.job_id:
        job = session.query(Job.title, Employee.company_name).join(Employee, Job.employee_id == Employee.employee_id).filter(Job.job_id == req.job_id).first()
        if not job:
            session.close()
            return {"message": "Job not found"}
        if status != "Wishlist":
            session.close()
            return {
                "message": "Portal jobs can only be saved as Wishlist here. "
                           "Use /apply_for_job to apply."
            }
        existing = session.query(TrackedJob).filter(TrackedJob.candidate_id == req.candidate_id,TrackedJob.job_id == req.job_id).first()
        if existing:
            session.close()
            return {"message": "This job is already in your tracker"}
        company, role, source = job.company_name, job.title, "Portal"
    elif company == "" or role == "":
        session.close()
        return {"message": "Give a job_id, or both company and role"}
    applied_date = req.applied_date
    if applied_date is None and status != "Wishlist":
        applied_date = date.today()
    tracked = TrackedJob(
        candidate_id=req.candidate_id,
        job_id=req.job_id,
        company=company,
        role=role,
        source=source,
        status=status,
        applied_date=applied_date,
        notes=req.notes
    )
    session.add(tracked)
    session.commit()
    tracked_id = tracked.tracked_id
    session.close()
    return {"message": "Added to tracker", "tracked_id": tracked_id}

@router.get("/my_jobs")
def my_tracked_jobs(candidate_id: int, status: Optional[str] = None):
    session = get_session()
    query = session.query(TrackedJob).filter(TrackedJob.candidate_id == candidate_id)
    if status:
        query = query.filter(TrackedJob.status == status)
    rows = query.order_by(TrackedJob.tracked_id.desc()).all()
    session.close()
    if not rows:
        return {"message": "Your tracker is empty."}
    return {
        "tracked_jobs": [
            {
                "tracked_id": r.tracked_id,
                "job_id": r.job_id,
                "company": r.company,
                "role": r.role,
                "source": r.source,
                "status": r.status,
                "applied_date": r.applied_date,
                "notes": r.notes,
            }
            for r in rows
        ]
    }

@router.get("/summary")
def tracker_summary(candidate_id: int):
    session = get_session()
    rows = session.query(TrackedJob.status).filter(TrackedJob.candidate_id == candidate_id).all()
    session.close()
    summary = {status: 0 for status in TRACKER_STATUSES}
    for (status,) in rows:
        if status in summary:
            summary[status] += 1
    return {"total": len(rows), "by_status": summary}

@router.put("/update/{tracked_id}")
def update_tracked_job(tracked_id: int, req: TrackUpdateRequest):
    if req.status is not None and req.status not in TRACKER_STATUSES:
        return {"message": f"Invalid status. Use: {', '.join(TRACKER_STATUSES)}"}
    session = get_session()
    tracked = session.query(TrackedJob).filter(TrackedJob.tracked_id == tracked_id, TrackedJob.candidate_id == req.candidate_id).first()
    if not tracked:
        session.close()
        return {"message": "Tracked job not found or does not belong to you"}
   
    if req.status is not None and tracked.job_id:
        portal_application = session.query(Application).filter(
            Application.job_id == tracked.job_id,
            Application.candidate_id == req.candidate_id
        ).first()
        if portal_application:
            session.close()
            return {
                "message": "This application is managed by the employer. "
                           "You can still update notes."
            }
    if req.status is not None:
        tracked.status = req.status
        if req.status != "Wishlist" and tracked.applied_date is None:
            tracked.applied_date = date.today()
    if req.applied_date is not None:
        tracked.applied_date = req.applied_date
    if req.notes is not None:
        tracked.notes = req.notes
    session.commit()
    session.close()
    return {"message": "Tracker updated successfully!"}


@router.delete("/delete/{tracked_id}")
def delete_tracked_job(tracked_id: int, candidate_id: int):
    session = get_session()
    tracked = session.query(TrackedJob).filter(
        TrackedJob.tracked_id == tracked_id,
        TrackedJob.candidate_id == candidate_id
    ).first()
    if not tracked:
        session.close()
        return {"message": "Tracked job not found or does not belong to you"}
    session.delete(tracked)
    session.commit()
    session.close()
    return {"message": "Removed from tracker"}