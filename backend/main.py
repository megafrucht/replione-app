from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from backend.email_bot import send_test_email

app = FastAPI(title="Email Test Service")

class EmailRequest(BaseModel):
    email: EmailStr

@app.post("/api/send-email")
def send_email(data: EmailRequest):
    success = send_test_email(data.email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email. Please check SMTP configuration.")
    return {"success": True, "message": "Email sent successfully"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
