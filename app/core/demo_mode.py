import asyncio
import random
from datetime import datetime

async def simulate_whatsapp_delivery(phone: str, template: str):
    """
    Simulates the behavior of Meta WhatsApp API for demo purposes.
    """
    # Realistic delay for demo effect
    await asyncio.sleep(0.8)
    
    # Random success vs failure (90% success rate for demo)
    is_success = random.random() < 0.90
    
    if is_success:
        return True, {
            "messaging_product": "whatsapp",
            "contacts": [{"input": phone, "wa_id": phone}],
            "messages": [{"id": f"wamid.HBIBG{random.randint(100000, 999999)}", "message_status": "accepted"}]
        }
    else:
        return False, {
            "error": {
                "message": "(#131030) Receiver is incapable of receiving this message",
                "type": "OAuthException",
                "code": 131030,
                "error_data": {"details": "Recipient phone number not in allowed list for test numbers."},
                "fbtrace_id": f"AzM{random.randint(1000, 9999)}p"
            }
        }
