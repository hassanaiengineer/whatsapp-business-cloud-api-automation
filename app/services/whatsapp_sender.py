import requests
import json
import logging
from app.core.config import settings
from app.core.demo_mode import simulate_whatsapp_delivery

logger = logging.getLogger(__name__)

async def send_whatsapp_template(to_phone: str, template_name: str, language_code: str, variables: list):
    """
    Core service to send WhatsApp templates, handling both Demo and Production modes.
    """
    # Check for Demo Mode
    if settings.DEMO_MODE:
        logger.info(f"[DEMO MODE] Simulating broadcast to {to_phone}")
        return await simulate_whatsapp_delivery(to_phone, template_name)

    # Production Mode (Meta Cloud API)
    url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    parameters = [{"type": "text", "text": str(v)} for v in variables]
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": [{"type": "body", "parameters": parameters}]
        }
    }
    
    import asyncio
    try:
        logger.info(f"[PROD MODE] Sending real broadcast to {to_phone}")
        response = await asyncio.to_thread(
            requests.post,
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        response_data = response.json()
        
        if response.status_code == 200:
            return True, response_data
        else:
            logger.error(f"Meta API Error: {response_data}")
            return False, response_data
            
    except Exception as e:
        logger.exception(f"Unexpected error calling Meta API: {str(e)}")
        return False, {"error": str(e)}
