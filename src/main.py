import argparse
import os
from .pdf.pdf_processor import extract_text_from_pdf
from .resolutions.extractor import extract_resolutions
from .resolutions.analyzer import analyze_resolutions
from .notification.email_sender import send_email_summary

def main():
    parser = argparse.ArgumentParser(description='PDF kormányhatározat feldolgozó')
    parser.add_argument('pdf_path', help='A feldolgozandó PDF fájl útvonala')
    parser.add_argument('--analyze', action='store_true', help='Önkormányzati tartalom elemzése')
    parser.add_argument('--email', action='store_true', help='Email küldése az eredményekről')
    args = parser.parse_args()
    
    # Ellenőrizzük, hogy létezik-e a fájl
    if not os.path.exists(args.pdf_path):
        print(f"Hiba: A megadott fájl nem létezik: {args.pdf_path}")
        return
    
    # PDF szöveg kinyerése
    print(f"PDF feldolgozása: {args.pdf_path}")
    pdf_text = extract_text_from_pdf(args.pdf_path)
    
    # Kormányhatározatok kinyerése
    print("Kormányhatározatok keresése...")
    resolutions = extract_resolutions(pdf_text)
    print(f"{len(resolutions)} kormányhatározat található.")
    
    # Kormányhatározatok listázása
    for i, resolution in enumerate(resolutions, 1):
        print(f"{i}. {resolution['title']}")
    
    # Elemzés, ha kérték
    if args.analyze:
        print("Önkormányzati tartalom elemzése...")
        results = analyze_resolutions(resolutions)
        print(f"{len(results['relevant_resolutions'])} releváns kormányhatározat található.")
        for res in results['relevant_resolutions']:
            print(f"Releváns kormányhatározat: {res['resolution']['title']}")            
            print(f"Relevancia pontszám: {res['relevance_score']}")
            print("Kulcsszó találatok:")
            for match in res['keyword_matches']:
                print(f"- Kulcsszó: {match['keyword']}, Cím találatok: {match['title_count']}, Tartalom találatok: {match['content_count']}")
            print(f"Összefoglaló: {res['summary']}")
        
        # Email küldése, ha kérték
        if args.email and results['relevant_resolutions']:
            print("Email küldése az eredményekről...")
            send_email_summary(results)
    
    print("Feldolgozás befejezve.")

if __name__ == "__main__":
    main()