import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from dotenv import load_dotenv

# Környezeti változók betöltése
load_dotenv()

def send_email_summary(results):
    """
    Email küldése az önkormányzatokat érintő kormányhatározatokról.
    """
    # Email beállítások betöltése környezeti változókból
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_list = os.getenv("RECIPIENT_LIST", "").split(",")
    
    if not sender_email or not sender_password or not recipient_list:
        print("Hiányzó email beállítások. Konfiguráld a .env fájlt.")
        return False
    
    # HTML sablon az email tartalmához
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .resolution { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }
            .title { font-weight: bold; }
            .summary { font-style: italic; color: #555; }
        </style>
    </head>
    <body>
        <h2>Önkormányzatokkal kapcsolatos kormányhatározatok</h2>
        <p>A legutóbbi Magyar Közlönyben {{ relevant_count }} olyan kormányhatározat található, amely önkormányzatokkal kapcsolatos.</p>
        
        {% for item in relevant_resolutions %}
        <div class="resolution">
            <div class="title">{{ item.resolution.title }}</div>
            <div class="date">Kiadva: {{ item.resolution.date }}</div>
            <div class="summary">
                <strong>Összefoglaló:</strong> {{ item.summary }}
            </div>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    # Sablon kitöltése adatokkal
    template = Template(html_template)
    html_content = template.render(
        relevant_count=len(results['relevant_resolutions']),
        relevant_resolutions=results['relevant_resolutions']
    )
    
    # Email összeállítása
    msg = MIMEMultipart()
    msg['Subject'] = f"Önkormányzati vonatkozású kormányhatározatok - {len(results['relevant_resolutions'])} találat"
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_list)
    
    msg.attach(MIMEText(html_content, 'html'))
    
    # Email küldése
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sikeresen elküldve {len(recipient_list)} címzettnek.")
        return True
    except Exception as e:
        print(f"Hiba az email küldése közben: {e}")
        return False