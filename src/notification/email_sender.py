from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from datetime import datetime

def send_email_summary(results):
    """
    Email küldése az önkormányzatokat érintő kormányhatározatokról.
    """
        
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
    msg = {
        'subject': f"Önkormányzati vonatkozású kormányhatározatok - {len(results['relevant_resolutions'])} találat",
        'body': html_content,
        'recipients': ["gallzoltan@gmail.com"],
        'bccRecipients': [],
        'ccRecipients': [],
        'attachments': [],
        'dateSending': datetime.now(),
    }
    
    
    # msg.attach(MIMEText(html_content, 'html'))
    
    # Email küldése
    