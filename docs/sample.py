import spacy
import PyPDF2
from pathlib import Path
from typing import List, Dict, Tuple, Set

class PdfContent:
    """PDF tartalom tárolására szolgáló osztály"""
    def __init__(self, oldal_szam: int, tartalom: str):
        self.oldal_szam = oldal_szam
        self.tartalom = tartalom
    
    def __str__(self):
        return f"Oldal: {self.oldal_szam}, Tartalom: {self.tartalom[:100]}..."

def pdf_oldalak_kinyerese(pdf_ut: str) -> List[str]:
    """PDF fájl oldalainak szövegének kinyerése"""
    oldalak = []
    try:
        with open(pdf_ut, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i in range(len(pdf_reader.pages)):
                oldal_szoveg = pdf_reader.pages[i].extract_text()
                oldalak.append(oldal_szoveg)
        return oldalak
    except Exception as e:
        print(f"Hiba történt a PDF olvasása közben: {e}")
        return []

def pontos_kereseses_talalatok(oldalak: List[str], keresesi_kifejezesek: List[str]) -> List[PdfContent]:
    """Java-hoz hasonló, pontos szövegrészlet-egyezésen alapuló keresés"""
    result = []
    for i, content in enumerate(oldalak):
        for kifejezés in keresesi_kifejezesek:
            if kifejezés.lower() in content.lower():
                pdfcontent = PdfContent(i+1, content)  # +1 a 0-tól kezdődő indexelés miatt
                result.append(pdfcontent)
                break  # Ha egy kifejezés talált, ne add többször hozzá ugyanazt az oldalt
    return result

def spacy_szemantikus_keresés(oldalak: List[str], 
                             keresesi_kifejezesek: List[str],
                             nlp, 
                             hasonlosagi_kuszob: float = 0.7) -> List[PdfContent]:
    """
    spaCy segítségével szemantikai alapú keresés az oldalak szövegében.
    Ez a keresési módszer megtalálja a hasonló jelentésű szövegrészeket is.
    """
    result = []
    
    # Keresési kifejezések előfeldolgozása
    keresesi_vektorok = [nlp(kifejezés) for kifejezés in keresesi_kifejezesek]
    
    # Oldalak feldolgozása
    for i, oldal_szoveg in enumerate(oldalak):
        # Oldal szövegének mondatokra bontása és feldolgozása
        doc = nlp(oldal_szoveg)
        
        talalt_egyezes = False
        
        # Pontos szövegrész egyezés keresése először (gyorsabb)
        for kifejezés in keresesi_kifejezesek:
            if kifejezés.lower() in oldal_szoveg.lower():
                result.append(PdfContent(i+1, oldal_szoveg))
                talalt_egyezes = True
                break
        
        # Ha nem volt pontos egyezés, szemantikai keresés végzése
        if not talalt_egyezes:
            # Mondatonként vizsgáljuk a szöveget
            mondatok = list(doc.sents)
            for mondat in mondatok:
                if len(mondat.text.strip()) < 10:  # Túl rövid mondatokat kihagyjuk
                    continue
                    
                # Mondatvektorok hasonlítása a keresett kifejezésekhez
                for keresesi_vektor in keresesi_vektorok:
                    hasonlosag = mondat.similarity(keresesi_vektor)
                    if hasonlosag >= hasonlosagi_kuszob:
                        result.append(PdfContent(i+1, oldal_szoveg))
                        talalt_egyezes = True
                        break
                
                if talalt_egyezes:
                    break
                    
    return result

def onkormanyzati_dokumentum_kereses(pdf_ut: str) -> List[PdfContent]:
    """
    Önkormányzati dokumentum keresése, a Java kódban szereplő
    mintához hasonló kifejezések alapján, spaCy használatával
    """
    # spaCy nyelvi modell betöltése
    nlp = spacy.load("hu_core_news_lg")  # Nagy magyar modell a jobb vektorokért
    
    # Oldalak kinyerése
    oldalak = pdf_oldalak_kinyerese(pdf_ut)
    if not oldalak:
        print("Nem sikerült oldalakat kinyerni a PDF-ből.")
        return []
    
    # más kifejezések, amiket keresni szeretnénk
    keresesi_kifejezesek = [
        "ix. helyi önkormányzatok",
        "települési önkormányzatok", 
        "önkormányzatok adósságot keletkeztető",
        "gazdasági társaságok adósságot keletkeztető",
        # Kibővített keresés - szemantikailag hasonló kifejezések
        "helyi önkormányzat",
        "önkormányzati adósság",
        "önkormányzati hitelfelvétel",
        "adósságot keletkeztető ügyletek"
    ]
    
    pontos_talalatok = pontos_kereseses_talalatok(oldalak, keresesi_kifejezesek)
    
    # spaCy szemantikus keresés (rugalmasabb, hasonló jelentésű szövegrészeket is megtalál)
    szemantikus_talalatok = spacy_szemantikus_keresés(
        oldalak, 
        keresesi_kifejezesek, 
        nlp,
        hasonlosagi_kuszob=0.75  # Állítható küszöbérték
    )
    
    # A találatok egyesítése és duplikátumok eltávolítása
    osszes_talalat = pontos_talalatok.copy()
    talalt_oldalak = {t.oldal_szam for t in pontos_talalatok}
    
    for talalat in szemantikus_talalatok:
        if talalat.oldal_szam not in talalt_oldalak:
            osszes_talalat.append(talalat)
            talalt_oldalak.add(talalat.oldal_szam)
    
    return osszes_talalat

if __name__ == "__main__":
    pdf_ut = "teszt_onkormanyzat.pdf"
    
    print(f"Önkormányzati dokumentumok keresése: {pdf_ut}")
    talalatok = onkormanyzati_dokumentum_kereses(pdf_ut)
    
    if talalatok:
        print(f"\nTalált oldalak száma: {len(talalatok)}")
        for i, talalat in enumerate(talalatok):
            print(f"\n{i+1}. találat - {talalat.oldal_szam}. oldal:")
            print(f"  Tartalom részlet: {talalat.tartalom[:150]}...")
    else:
        print("Nem található önkormányzati dokumentum.")