import os
import sqlite3
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class GazetteFetcher:
    """Magyar Közlöny letöltő osztály"""
    
    FEED_URL = "https://magyarkozlony.hu/feed"
    DB_FILE = "gazettes.db"
    DOWNLOAD_DIR = "downloads"
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Inicializálja a Magyar Közlöny letöltőt
        
        Args:
            base_dir: Alap könyvtár, ahol az adatbázist és letöltéseket tárolja
                     Ha nincs megadva, az aktuális munkakönyvtárat használja
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path.cwd()
            
        # Adatbázis és letöltési könyvtár elérési útvonala
        self.db_path = self.base_dir / self.DB_FILE
        self.download_path = self.base_dir / self.DOWNLOAD_DIR
        
        # Letöltési könyvtár létrehozása, ha nem létezik
        if not self.download_path.exists():
            self.download_path.mkdir(parents=True)
            
        # Adatbázis inicializálása
        self._init_database()
        
    def _init_database(self):
        """Adatbázis inicializálása, ha még nem létezik"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gazettes (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            publication_date TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL,
            download_date TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def fetch_feed(self) -> List[Dict]:
        """
        RSS feed letöltése és feldolgozása
        
        Returns:
            A Magyar Közlöny bejegyzések listája
        """
        try:
            response = requests.get(self.FEED_URL)
            response.raise_for_status()
            
            # XML feldolgozása
            root = ET.fromstring(response.content)
            
            # RSS névtér kezelése
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # Bejegyzések kinyerése
            entries = []
            for entry in root.findall('.//atom:entry', namespaces):
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text if title_elem is not None else ""
                
                # Csak a Magyar Közlöny bejegyzéseket szűrjük
                if "Magyar Közlöny" in title:
                    link_elem = entry.find('atom:link[@rel="alternate"]', namespaces)
                    url = link_elem.get('href') if link_elem is not None else ""
                    
                    published_elem = entry.find('atom:published', namespaces)
                    published = published_elem.text if published_elem is not None else ""
                    
                    entries.append({
                        'title': title,
                        'url': url,
                        'published': published
                    })
            
            return entries
            
        except Exception as e:
            logger.error(f"Hiba történt az RSS feed lekérése közben: {e}")
            return []
    
    def is_already_downloaded(self, url: str) -> bool:
        """
        Ellenőrzi, hogy egy adott URL-t már letöltöttünk-e
        
        Args:
            url: Az ellenőrizendő URL
            
        Returns:
            True, ha már letöltöttük, egyébként False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM gazettes WHERE url = ?", (url,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result is not None
    
    def download_gazette(self, entry: Dict) -> Tuple[bool, Optional[str]]:
        """
        Magyar Közlöny letöltése
        
        Args:
            entry: A letöltendő közlöny adatai
            
        Returns:
            Tuple (sikeres letöltés, fájlnév vagy None)
        """
        if self.is_already_downloaded(entry['url']):
            logger.info(f"A közlöny már le volt töltve: {entry['title']}")
            return False, None
        
        try:
            # PDF URL kinyerése (ha az entry['url'] nem közvetlenül PDF-re mutat)
            if entry['url'].endswith('.pdf'):
                pdf_url = entry['url']
            else:
                # Ha szükséges, itt lehet kiegészítő logika a PDF URL kinyeréséhez
                # a közlöny oldalából
                pdf_url = entry['url']
            
            # Fájlnév generálás a címből
            filename = self._generate_filename(entry['title'])
            filepath = self.download_path / filename
            
            # PDF letöltése
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Mentés az adatbázisba
            self._save_to_database(entry, filename)
            
            logger.info(f"Sikeresen letöltve: {entry['title']} -> {filename}")
            return True, filename
            
        except Exception as e:
            logger.error(f"Hiba történt a letöltés közben: {e}")
            return False, None
    
    def _generate_filename(self, title: str) -> str:
        """Fájlnév generálása a címből"""
        # Cím tisztítása fájlnévhez
        clean_title = "".join(c if c.isalnum() or c in "._- " else "_" for c in title)
        clean_title = clean_title.replace(" ", "_")
        
        # Időbélyeg hozzáadása az egyediség érdekében
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        return f"{clean_title}_{timestamp}.pdf"
    
    def _save_to_database(self, entry: Dict, filename: str) -> None:
        """
        Letöltött közlöny mentése az adatbázisba
        
        Args:
            entry: A közlöny adatai
            filename: A letöltött fájl neve
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO gazettes (title, publication_date, url, filename, download_date) VALUES (?, ?, ?, ?, ?)",
            (entry['title'], entry['published'], entry['url'], filename, now)
        )
        
        conn.commit()
        conn.close()
    
    def fetch_new_gazettes(self) -> List[str]:
        """
        Új Magyar Közlönyök letöltése
        
        Returns:
            A sikeresen letöltött fájlok listája
        """
        downloaded_files = []
        
        # RSS feed letöltése
        entries = self.fetch_feed()
        
        if not entries:
            logger.warning("Nem találhatók Magyar Közlöny bejegyzések a feed-ben")
            return downloaded_files
        
        # Közlönyök letöltése, amelyek még nem voltak letöltve
        for entry in entries:
            success, filename = self.download_gazette(entry)
            if success and filename:
                downloaded_files.append(str(self.download_path / filename))
                
        return downloaded_files


def main():
    """Fő futtatható funkció"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Alapértelmezett könyvtár használata
    fetcher = GazetteFetcher()
    
    # Új közlönyök letöltése
    downloaded = fetcher.fetch_new_gazettes()
    
    if downloaded:
        print(f"{len(downloaded)} új Magyar Közlöny került letöltésre:")
        for filename in downloaded:
            print(f"- {filename}")
    else:
        print("Nem került letöltésre új Magyar Közlöny.")


if __name__ == "__main__":
    main()