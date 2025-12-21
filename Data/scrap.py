import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import numpy as np

# --- Configuration et variables globales ---
VILLES = ["casablanca"] # Laissez cette ligne pour le test, remettez la liste complète après
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
TIMEOUT = 30 # Augmenté à 30 secondes
PAUSE_PAGE = 1.0 # Augmenté à 1.0 seconde entre les pages
PAUSE_ANNONCE = 1.0 # Augmenté à 1.0 seconde entre les annonces

# Définition des colonnes finales pour initialisation (SOLUTION 1)
COLONNES_FINALES = [
    'Ville', 'Quartier', 'Prix', 'Type de Bien', 'Surface', 
    'Nombre de Pièces', 'Nombre de Chambres', 'Nombre de Salles de Bain', 
    'Étage', 'État', 
    'Terrasse', 'Garage', 'Ascenseur', 'Piscine', 'Sécurité'
]

def extract_details(soup, link):
    """
    Extrait les détails spécifiques d'une page d'annonce Mubawab.
    (Fonction de détails non modifiée pour éviter de réintroduire des bugs)
    """
    
    details = {
        'Prix': 'Nan', 'Type de Bien': 'Nan', 'Surface': 'Nan', 
        'Nombre de Pièces': 'Nan', 'Nombre de Chambres': 'Nan', 
        'Nombre de Salles de Bain': 'Nan', 'Étage': 'Nan', 
        'État': 'Nan', 'Quartier': 'Nan', 'Lien': link, 
        'Ville_Reelle': 'Nan', # Doit être présent
        'Terrasse': 'Non', 'Garage': 'Non', 'Ascenseur': 'Non', 
        'Piscine': 'Non', 'Sécurité': 'Non',
    }
    
    # ... Reste de la logique d'extraction (non affiché pour la concision) ...

    # 1. Extraction du Prix
    v_prix = soup.find('h3', {"class": "orangeTit"})
    if v_prix:
        details['Prix'] = v_prix.text.strip().replace('\xa0', ' ')
        
    # 2. Localisation (Ville_Reelle et Quartier)
    loc_span = soup.find('span', {"class": "listingH3"})
    if loc_span:
        loc_text = loc_span.text.strip().replace('\n', ', ').replace('\t', '')
        parts = loc_text.split(",")
        details['Ville_Reelle'] = parts[-1].strip() if len(parts) > 0 else 'Nan'
        details['Quartier'] = parts[0].strip() if len(parts) > 1 else 'Nan'
    
    if details['Quartier'] == 'Nan' or details['Ville_Reelle'] == 'Nan':
        loc_h3 = soup.find('h3', {"class": "greyTit"})
        if loc_h3:
            loc_text_h3 = loc_h3.text.strip()
            match = re.search(r'(.+)\s+à\s+(.+)', loc_text_h3, re.IGNORECASE)
            if match:
                details['Quartier'] = match.group(1).strip()
                details['Ville_Reelle'] = match.group(2).strip()
            elif loc_text_h3:
                 parts = loc_text_h3.split(",")
                 details['Ville_Reelle'] = parts[-1].strip() if len(parts) > 0 else 'Nan'
                 details['Quartier'] = parts[0].strip() if len(parts) > 1 else 'Nan'


    # 3. Extraction des Features Détaillées (Type de Bien, État, Étage)
    feature_containers = soup.find_all('div', class_='adMainFeature col-4')
    for container in feature_containers:
        label_element = container.find('p', class_='adMainFeatureContentLabel')
        value_element = container.find('p', class_='adMainFeatureContentValue')
        
        if label_element and value_element:
            label = label_element.text.strip()
            value = value_element.text.strip()

            if label == "Type de bien": details['Type de Bien'] = value
            elif label == "Étage du bien": details['Étage'] = value
            elif label == "État": details['État'] = value
            
    # 4. Attributs Primaires (Surface, Pièces, SDB)
    attribute_features = soup.find_all('div', {"class": "adDetailFeature"})
    for feature_div in attribute_features:
        text = feature_div.text.strip()
        if "m²" in text:
            details['Surface'] = text.split('\n')[0].strip()
        elif "Pièce" in text:
            details['Nombre de Pièces'] = text.split('\n')[0].strip()
        elif "Chambre" in text:
            details['Nombre de Chambres'] = text.split('\n')[0].strip()
        elif "bain" in text:
            details['Nombre de Salles de Bain'] = text.split('\n')[0].strip()
            
    # 5. Caractéristiques Supplémentaires (Binaires) - LOGIQUE V11
    CARACS_BINAIRES = {
        'Terrasse': 'Terrasse', 'Garage': 'Garage', 'Ascenseur': 'Ascenseur', 
        'Piscine': 'Piscine', 'Sécurité': 'Sécurité', 
    }
    
    all_features_spans = soup.find_all('span', class_='fSize11 centered')
    
    for span in all_features_spans:
        t = span.text.strip()
        for keyword, detail_key in CARACS_BINAIRES.items():
            if keyword.lower() in t.lower():
                details[detail_key] = "Oui"

    return details


def scrape_mubawab_immo_v13():
    """Fonction principale de scraping avec gestion d'erreurs."""
    start_time = time.time()
    all_data = []
    
    MAX_PAGES_FORCE = 250 
    MAX_PAGES_ABSOLUE = 1000 

    for ville in VILLES:
        liens = []
        base_url_list = f"https://www.mubawab.ma/fr/ct/{ville}/immobilier-a-vendre-all:p:1"

        print(f"\n--- Démarrage du scraping pour {ville.upper()} ---")

        # 1. Collecte des liens avec pagination
        try:
            # Requête initiale pour l'estimation
            page = requests.get(base_url_list, headers=HEADERS, timeout=TIMEOUT)
            page.raise_for_status() # Lève une erreur si la page n'est pas trouvée (404)
            soup = BeautifulSoup(page.content, "html.parser")
            
            v_nb_de_pages = soup.find('p', {"class": "fSize11 centered"})
            nb_pages_estime = 1
            if v_nb_de_pages:
                match = re.search(r'(\d+)(?=\s*pages)', v_nb_de_pages.text.strip())
                nb_pages_estime = int(match.group(1)) if match else 1
            
            max_pages = max(nb_pages_estime, MAX_PAGES_FORCE)
            max_pages = min(max_pages, MAX_PAGES_ABSOLUE)
            
            print(f"Estimation des pages: {nb_pages_estime}. Forçage du scraping jusqu'à {max_pages} pages.")
            
            for k in range(1, max_pages + 1):
                url_page = f"https://www.mubawab.ma/fr/ct/{ville}/immobilier-a-vendre-all:p:{k}"
                
                # --- GESTION DE LA REQUÊTE ET DU TIMEOUT (SOLUTION 2) ---
                try:
                    page = requests.get(url_page, headers=HEADERS, timeout=TIMEOUT)
                    page.raise_for_status()
                    soup = BeautifulSoup(page.content, "html.parser")
                except requests.exceptions.RequestException as req_err:
                    print(f"Erreur de connexion/timeout pour la page {k}: {req_err}. Passage à la page suivante.")
                    time.sleep(PAUSE_PAGE * 2) # Pause plus longue en cas d'erreur
                    continue 

                var_de_annonce = soup.find_all('h2', {"class": "listingTit"})
                
                if not var_de_annonce:
                    print(f"Arrêt de la pagination pour {ville} à la page {k-1} (page {k} vide).")
                    break 
                    
                for h2 in var_de_annonce:
                    a_tag = h2.find("a")
                    if a_tag and a_tag.attrs.get("href"):
                        lien_complet = a_tag.attrs["href"] if a_tag.attrs["href"].startswith("http") else "https://www.mubawab.ma" + a_tag.attrs["href"]
                        liens.append(lien_complet)
                
                time.sleep(PAUSE_PAGE) # Pause entre les pages

            print(f"Total de {len(liens)} liens d'annonces collectés pour {ville}.")

        except Exception as e:
            print(f"Erreur lors de la collecte des liens pour {ville}: {e}")
            continue

        # 2. Extraction des détails de chaque annonce
        for i, lien in enumerate(liens):
            try:
                page = requests.get(lien, headers=HEADERS, timeout=TIMEOUT)
                page.raise_for_status()
                soup = BeautifulSoup(page.content, "html.parser")
                
                details = extract_details(soup, lien)
                details['Ville_Boucle'] = ville
                all_data.append(details)
                
                if (i + 1) % 50 == 0:
                     print(f"  -> {i+1} annonces traitées pour {ville}")

                time.sleep(PAUSE_ANNONCE) # Pause entre les annonces

            except Exception as e:
                print(f"Erreur (détails) au lien n°{i+1} ({lien}): {e}. Annonce ignorée.")
                # Assurez-vous d'avoir les colonnes pour les annonces ignorées
                default_data = {
                    'Ville_Boucle': ville, 'Lien': lien, 'Prix': 'Nan', 'Type de Bien': 'Nan', 'Quartier': 'Nan',
                    'Surface': 'Nan', 'Nombre de Pièces': 'Nan', 'Nombre de Chambres': 'Nan', 
                    'Nombre de Salles de Bain': 'Nan', 'Étage': 'Nan', 'État': 'Nan',
                    'Terrasse': 'Non', 'Garage': 'Non', 'Ascenseur': 'Non', 'Piscine': 'Non', 'Sécurité': 'Non',
                    'Ville_Reelle': 'Nan' # Doit être présent
                }
                all_data.append(default_data)


    # 3. Finalisation du DataFrame
    
    # SOLUTION 1: Initialisation du DataFrame si all_data est vide
    if not all_data:
        print("Avertissement: Aucun lien n'a pu être collecté. Création d'un DataFrame vide.")
        df = pd.DataFrame(columns=COLONNES_FINALES)
        df.to_csv("Mubawab_Vente_Data_V13_FINAL.csv", index=False, encoding='utf-8-sig')
        return df
        
    df = pd.DataFrame(all_data)
    
    # Remplissage des villes
    # Cette étape est désormais sécurisée car df n'est pas vide ou contient déjà les colonnes de 'default_data'
    df['Ville'] = df['Ville_Reelle'].apply(lambda x: x if x != 'Nan' and x is not None else np.nan)
    df['Ville'] = df['Ville'].fillna(df['Ville_Boucle'])
    df = df.drop(columns=['Ville_Reelle', 'Ville_Boucle', 'Lien'])
    
    # Réorganisation des colonnes
    df = df.reindex(columns=COLONNES_FINALES)

    df.to_csv("Mubawab_Vente_Data_V13_FINAL.csv", index=False, encoding='utf-8-sig')
    
    end_time = time.time()
    print(f"\n✅ Scraping terminé. Total de {len(df)} annonces enregistrées dans 'Mubawab_Vente_Data_V13_FINAL.csv'.")
    print(f"Durée totale: {(end_time - start_time)/60:.2f} minutes.")
    
    return df

if __name__ == '__main__':
    # Correction de la faute de frappe __name__ (SOLUTION 3)
    data_scraped = scrape_mubawab_immo_v13()
    print("\nExtraction des premières lignes du DataFrame :")
    print(data_scraped.head())