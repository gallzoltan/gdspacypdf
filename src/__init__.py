"""
gdspacypdf - A Magyar Közlöny önkormányzatokra vonatkozó tartalom elemzése
"""

__version__ = "0.1.0"

# Főbb függvények importálása könnyű hozzáféréshez
from .pdf.pdf_processor import extract_text_from_pdf
from .resolutions.extractor import extract_resolutions
from .resolutions.analyzer import analyze_resolutions
from .notification.email_sender import send_email_summary

# Exportált funkciók listája
__all__ = [
    'extract_text_from_pdf',
    'extract_resolutions',
    'analyze_resolutions',
    'send_email_summary',
]