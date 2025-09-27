import json
import sys
import pandas as pd
import os
import unicodedata

# Votre classe IndicateursManager (adaptée)
class IndicateursManager:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = self.load_data()
    
    def load_data(self):
        """Charge les données depuis le fichier Excel"""
        try:
            if os.path.exists(self.excel_path):
                df = pd.read_excel(self.excel_path)
                df.columns = df.columns.str.strip()
                
                if 'image_troncon' not in df.columns:
                    df['image_troncon'] = ''
                if 'image_taudis' not in df.columns:
                    df['image_taudis'] = ''
                    
                return df
            else:
                return self.create_sample_data()
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return self.create_sample_data()
    
    def create_sample_data(self):
        """Crée des données d'exemple"""
        sample_data = {
            'Ville': ['Douala', 'Douala', 'Yaoundé', 'Yaoundé'],
            'Nom de la Commune': ['Douala 1', 'Douala 2', 'Yaoundé 1', 'Yaoundé 2'],
            'tronçon de voirie': ['Boulevard 1', 'Rue 2', 'Avenue 3', 'Boulevard 4'],
            'linéaire de voirie(ml)': [2500, 1200, 3200, 1800],
            'Nom de la poche du quartier de taudis': ['Quartier A', 'Quartier B', 'Quartier C', 'Quartier D'],
            'superficie de la poche du quartier de taudis': [12500, 8500, 9800, 7600],
            'présence du nid de poule': ['Oui', 'Non', 'Oui', 'Non'],
            'classe de voirie': ['Primaire', 'Secondaire', 'Primaire', 'Secondaire'],
            'Nombre de point lumineux sur le tronçon': [45, 28, 62, 35],
            'image_troncon': ['', '', '', ''],
            'image_taudis': ['', '', '', '']
        }
        return pd.DataFrame(sample_data)
    
    def remove_accents(self, text):
        """Supprime les accents d'un texte pour la normalisation"""
        if pd.isna(text):
            return ""
        text_str = str(text)
        return ''.join(c for c in unicodedata.normalize('NFD', text_str) 
                      if unicodedata.category(c) != 'Mn')
    
    def normaliser_texte(self, texte):
        if pd.isna(texte):
            return ""
        texte_str = str(texte).strip().lower()
        return self.remove_accents(texte_str)
    
    def get_villes(self):
        villes = self.df['Ville'].dropna().unique()
        return sorted(list(set(villes)))
    
    def get_communes(self, ville):
        if not ville:
            return []
        ville_recherchee = self.normaliser_texte(ville)
        mask = self.df['Ville'].apply(self.normaliser_texte) == ville_recherchee
        communes = self.df.loc[mask, 'Nom de la Commune'].dropna().unique().tolist()
        return sorted(communes)
    
    def get_indicateurs_commune(self, commune):
        if not commune:
            return None
        
        commune_cleaned = self.normaliser_texte(commune)
        mask = self.df['Nom de la Commune'].apply(self.normaliser_texte) == commune_cleaned
        commune_data = self.df[mask]
        
        if len(commune_data) == 0:
            return None
        
        return {
            'commune': commune,
            'ville': commune_data['Ville'].iloc[0],
            'nombre_troncons': len(commune_data),
            'troncons_voirie': self.preparer_troncons_voirie(commune_data),
            'quartiers_taudis': self.preparer_quartiers_taudis(commune_data)
        }
    
    def preparer_troncons_voirie(self, data):
        troncons = []
        for _, row in data.iterrows():
            # Gérer les valeurs NaN
            nom = row.get('tronçon de voirie', 'Nom non disponible')
            if pd.isna(nom):
                nom = 'Nom non disponible'
                
            classe = row.get('classe de voirie', 'Non spécifiée')
            if pd.isna(classe):
                classe = 'Non spécifiée'
                
            image = row.get('image_troncon', '')
            if pd.isna(image):
                image = ''
            
            troncon = {
                'nom': nom,
                'lineaire_ml': float(row.get('linéaire de voirie(ml)', 0)),
                'classe': classe,
                'image': image
            }
            troncons.append(troncon)
        return troncons
    
    def preparer_quartiers_taudis(self, data):
        try:
            quartiers = []
            for _, row in data.iterrows():
                nom = row.get('Nom de la poche du quartier de taudis', '')
                if pd.isna(nom):
                    continue
                    
                image = row.get('image_taudis', '')
                if pd.isna(image):
                    image = ''
                
                quartier = {
                    'nom': nom,
                    'superficie_m2': float(row.get('superficie de la poche du quartier de taudis', 0)),
                    'image': image
                }
                quartiers.append(quartier)
            return quartiers
        except Exception as e:
            print(f"Erreur dans preparer_quartiers_taudis: {e}")
            return []

# Initialisation globale
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, 'indicateurs_urbains.xlsx')
indicateurs_manager = IndicateursManager(excel_path)

def handle_request(event_json):
    """Gère la requête Netlify Function"""
    path = event_json.get('path', '')
    http_method = event_json.get('httpMethod', 'GET')
    query_params = event_json.get('queryStringParameters', {}) or {}
    
    print(f"Requête reçue: {path} {http_method} {query_params}")
    
    # Routes API
    if path == '/api/villes' and http_method == 'GET':
        return {'villes': indicateurs_manager.get_villes()}, 200
    
    elif path == '/api/communes' and http_method == 'GET':
        ville = query_params.get('ville', '')
        return {'communes': indicateurs_manager.get_communes(ville)}, 200
    
    elif path == '/api/indicateurs' and http_method == 'GET':
        commune = query_params.get('commune', '')
        indicateurs = indicateurs_manager.get_indicateurs_commune(commune)
        if indicateurs is None:
            return {'error': 'Commune non trouvée'}, 404
        return indicateurs, 200
    
    else:
        return {'error': 'Route non trouvée'}, 404

if __name__ == '__main__':
    # Point d'entrée pour Netlify Functions
    if len(sys.argv) > 1:
        event_json = json.loads(sys.argv[1])
        try:
            result, status_code = handle_request(event_json)
            output = {
                'statusCode': status_code,
                'body': result
            }
            print(json.dumps(output))
        except Exception as e:
            error_output = {
                'statusCode': 500,
                'body': {'error': str(e)}
            }
            print(json.dumps(error_output))
    else:
        # Test local
        test_event = {
            'path': '/api/villes',
            'httpMethod': 'GET',
            'queryStringParameters': {}
        }
        result, status_code = handle_request(test_event)
        print("Test local:", result)