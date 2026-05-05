import json
import asyncio
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import models
from app.db.database import engine, get_db
from app.core.config import settings
from app.services.whatsapp_sender import send_whatsapp_template

# Initialize Database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# Mount Static and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class CampaignRequest(BaseModel):
    template_name: str
    language: str = "en_US"
    numbers: List[str]
    variables: List[str]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "demo_mode": settings.DEMO_MODE
    })

@app.post("/api/send-campaign")
async def send_campaign(campaign_data: CampaignRequest, db: Session = Depends(get_db)):
    """
    Handle campaign broadcast requests.
    """
    # 1. Create Campaign
    campaign = models.Campaign(
        template_name=campaign_data.template_name,
        language=campaign_data.language,
        is_demo="true" if settings.DEMO_MODE else "false"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    results = {"sent": 0, "failed": 0, "logs": []}
    
    # 2. Process Numbers
    for phone in campaign_data.numbers:
        clean_phone = phone.strip().replace("+", "").replace(" ", "")
        if not clean_phone: continue
        
        success, response = await send_whatsapp_template(
            to_phone=clean_phone,
            template_name=campaign_data.template_name,
            language_code=campaign_data.language,
            variables=campaign_data.variables
        )
        
        # 3. Log Result
        now = datetime.utcnow()
        log = models.MessageLog(
            campaign_id=campaign.id,
            phone=clean_phone,
            status="sent" if success else "failed",
            response=json.dumps(response),
            timestamp=now
        )
        db.add(log)
        
        if success: results["sent"] += 1
        else: results["failed"] += 1
            
        results["logs"].append({
            "phone": clean_phone,
            "status": log.status,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    db.commit()
    return results

@app.get("/api/logs")
async def get_logs(db: Session = Depends(get_db)):
    """
    Fetch recent message logs for the UI.
    """
    logs = db.query(models.MessageLog).order_by(models.MessageLog.timestamp.desc()).limit(50).all()
    formatted_logs = []
    for log in logs:
        try:
            response_data = json.loads(log.response) if log.response else {}
        except json.JSONDecodeError:
            response_data = {"error": "Invalid JSON data in database"}
            
        formatted_logs.append({
            "id": log.id,
            "phone": log.phone,
            "status": log.status,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "response": response_data
        })
    return formatted_logs
