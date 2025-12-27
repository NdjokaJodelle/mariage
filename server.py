#!/usr/bin/env python3
"""
Serveur Python simple pour l'application de mariage
Gère le listing et l'upload de fichiers dans le dossier media/
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import cgi
from urllib.parse import urlparse

MEDIA_FOLDER = 'media'
INFO_FILE = 'info.json'
INVITE_FILE = 'invite.json'
COMMENTAIRE_FILE = 'commentaire.json'
PORT = 8000

class WeddingHandler(SimpleHTTPRequestHandler):
    
    def end_headers(self):
        """Ajouter les headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        SimpleHTTPRequestHandler.end_headers(self)
    
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS (CORS preflight)"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        parsed_path = urlparse(self.path)
        
        # API pour lister les médias
        if parsed_path.path == '/api/media':
            self.list_media()
            return
        
        # API pour lister les alertes info
        if parsed_path.path == '/api/info':
            self.list_info()
            return
        
        # Sinon servir les fichiers statiques
        SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Gérer les requêtes POST (upload)"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/media/upload':
            self.upload_media()
            return
        
        if parsed_path.path == '/api/info/add':
            self.add_info()
            return
        
        self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        """Gérer les requêtes DELETE"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/media/'):
            filename = parsed_path.path.split('/')[-1]
            self.delete_media(filename)
            return
        
        if parsed_path.path.startswith('/api/info/'):
            alert_id = parsed_path.path.split('/')[-1]
            self.delete_info(alert_id)
            return
        
        self.send_error(404, "Not Found")
    
    def list_media(self):
        """Lister tous les médias du dossier media/"""
        try:
            print("📋 Demande de liste des médias...")
            
            # Créer le dossier s'il n'existe pas
            if not os.path.exists(MEDIA_FOLDER):
                os.makedirs(MEDIA_FOLDER)
                print(f"📁 Dossier {MEDIA_FOLDER}/ créé")
            
            media_list = []
            
            # Lister tous les fichiers
            for filename in os.listdir(MEDIA_FOLDER):
                filepath = os.path.join(MEDIA_FOLDER, filename)
                
                # Ignorer les dossiers et fichiers cachés
                if os.path.isdir(filepath) or filename.startswith('.'):
                    continue
                
                # Déterminer le type de média
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                    media_type = 'image'
                elif ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv']:
                    media_type = 'video'
                else:
                    continue  # Ignorer les autres types
                
                # Récupérer la date de modification
                timestamp = int(os.path.getmtime(filepath) * 1000)
                
                media_list.append({
                    'filename': filename,
                    'type': media_type,
                    'timestamp': timestamp,
                    'url': f'{MEDIA_FOLDER}/{filename}'
                })
            
            # Trier par date décroissante
            media_list.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Envoyer la réponse JSON
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_data = json.dumps({'media': media_list}, indent=2)
            self.wfile.write(response_data.encode('utf-8'))
            
            print(f"✅ Liste envoyée: {len(media_list)} fichier(s)")
            
        except Exception as e:
            print(f"❌ Erreur lors du listing: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")
    
    def list_info(self):
        """Lister toutes les alertes info"""
        try:
            print("📋 Demande de liste des alertes...")
            
            # Créer le fichier s'il n'existe pas
            if not os.path.exists(INFO_FILE):
                with open(INFO_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'alerts': []}, f, indent=2)
                print(f"📁 Fichier {INFO_FILE} créé")
            
            # Lire le fichier
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            alerts = data.get('alerts', [])
            
            # Envoyer la réponse JSON
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_data = json.dumps({'alerts': alerts}, indent=2, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
            
            print(f"✅ Liste envoyée: {len(alerts)} alerte(s)")
            
        except Exception as e:
            print(f"❌ Erreur lors du listing des alertes: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")
    
    def add_info(self):
        """Ajouter une nouvelle alerte info"""
        try:
            print("📢 Ajout d'une nouvelle alerte...")
            
            # Lire le contenu JSON
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            message = data.get('message', '').strip()
            
            if not message:
                self.send_error(400, "Message vide")
                return
            
            print(f"   Message: {message}")
            
            # Créer le fichier s'il n'existe pas
            if not os.path.exists(INFO_FILE):
                with open(INFO_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'alerts': []}, f, indent=2)
            
            # Lire les alertes existantes
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            alerts = file_data.get('alerts', [])
            
            # Créer la nouvelle alerte
            import time
            new_alert = {
                'id': int(time.time() * 1000),  # Timestamp en millisecondes
                'message': message,
                'timestamp': int(time.time() * 1000)
            }
            
            # Ajouter au début
            alerts.insert(0, new_alert)
            
            # Limiter à 50 alertes max
            if len(alerts) > 50:
                alerts = alerts[:50]
            
            # Sauvegarder
            with open(INFO_FILE, 'w', encoding='utf-8') as f:
                json.dump({'alerts': alerts}, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Alerte ajoutée (ID: {new_alert['id']})")
            
            # Réponse de succès
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_data = json.dumps({
                'success': True,
                'alert': new_alert
            }, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de l'alerte: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")
    
    def delete_info(self, alert_id):
        """Supprimer une alerte info"""
        try:
            print(f"🗑️ Suppression de l'alerte: {alert_id}")
            
            if not os.path.exists(INFO_FILE):
                self.send_error(404, "Fichier info.json non trouvé")
                return
            
            # Lire les alertes
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            alerts = data.get('alerts', [])
            alert_id_int = int(alert_id)
            
            # Filtrer
            new_alerts = [a for a in alerts if a['id'] != alert_id_int]
            
            if len(new_alerts) == len(alerts):
                print(f"❌ Alerte {alert_id} non trouvée")
                self.send_error(404, "Alerte non trouvée")
                return
            
            # Sauvegarder
            with open(INFO_FILE, 'w', encoding='utf-8') as f:
                json.dump({'alerts': new_alerts}, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Alerte {alert_id} supprimée")
            
            # Réponse de succès
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_data = json.dumps({'success': True})
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")
    
    def upload_media(self):
        """Upload un fichier média"""
        try:
            print("📤 Réception d'un fichier...")
            
            # Créer le dossier s'il n'existe pas
            if not os.path.exists(MEDIA_FOLDER):
                os.makedirs(MEDIA_FOLDER)
                print(f"📁 Dossier {MEDIA_FOLDER}/ créé")
            
            # Parser le formulaire multipart
            content_type = self.headers.get('Content-Type', '')
            
            if not content_type.startswith('multipart/form-data'):
                print(f"❌ Mauvais Content-Type: {content_type}")
                self.send_error(400, "Content-Type doit être multipart/form-data")
                return
            
            print(f"   Content-Type: {content_type}")
            
            # Parser avec cgi.FieldStorage
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            # Récupérer le fichier
            if 'file' not in form:
                print("❌ Pas de champ 'file' dans le formulaire")
                self.send_error(400, "Aucun fichier uploadé")
                return
            
            file_item = form['file']
            
            # Vérifier que c'est bien un fichier
            if not file_item.filename:
                print("❌ Nom de fichier vide")
                self.send_error(400, "Nom de fichier invalide")
                return
            
            print(f"   Fichier reçu: {file_item.filename}")
            
            # Récupérer la légende
            caption = form.getvalue('caption', '')
            if caption:
                print(f"   Légende: {caption}")
            
            # Sécuriser le nom de fichier
            filename = os.path.basename(file_item.filename)
            
            # Vérifier l'extension
            ext = os.path.splitext(filename)[1].lower()
            allowed_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
                '.mp4', '.webm', '.mov', '.avi', '.mkv'
            ]
            
            if ext not in allowed_extensions:
                print(f"❌ Extension {ext} non autorisée")
                self.send_error(400, f"Extension {ext} non autorisée")
                return
            
            # Chemin complet
            filepath = os.path.join(MEDIA_FOLDER, filename)
            
            # Si le fichier existe déjà, ajouter un numéro
            if os.path.exists(filepath):
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filename = f"{base}_{counter}{extension}"
                    filepath = os.path.join(MEDIA_FOLDER, filename)
                    counter += 1
                print(f"   Fichier renommé en: {filename}")
            
            # Sauvegarder le fichier
            with open(filepath, 'wb') as f:
                f.write(file_item.file.read())
            
            file_size = os.path.getsize(filepath)
            print(f"✅ Fichier sauvegardé: {filename} ({file_size} bytes)")
            
            # Réponse de succès
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_data = json.dumps({
                'success': True,
                'filename': filename,
                'caption': caption
            })
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Erreur lors de l'upload: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")
    
    def delete_media(self, filename):
        """Supprimer un fichier média"""
        try:
            print(f"🗑️ Demande de suppression: {filename}")
            
            # Sécuriser le nom de fichier
            filename = os.path.basename(filename)
            filepath = os.path.join(MEDIA_FOLDER, filename)
            
            if not os.path.exists(filepath):
                print(f"❌ Fichier non trouvé: {filepath}")
                self.send_error(404, "Fichier non trouvé")
                return
            
            # Supprimer le fichier
            os.remove(filepath)
            print(f"✅ Fichier supprimé: {filename}")
            
            # Réponse de succès
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_data = json.dumps({'success': True})
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Erreur serveur: {str(e)}")


def run_server():
    """Démarrer le serveur"""
    
    # Vérifier que le dossier media existe
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
        print(f"📁 Dossier {MEDIA_FOLDER}/ créé")
    
    # Créer le fichier info.json s'il n'existe pas
    if not os.path.exists(INFO_FILE):
        with open(INFO_FILE, 'w', encoding='utf-8') as f:
            json.dump({'alerts': []}, f, indent=2)
        print(f"📁 Fichier {INFO_FILE} créé")
    
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, WeddingHandler)
    
    print("=" * 70)
    print("🎉 SERVEUR DE MARIAGE DÉMARRÉ !")
    print("=" * 70)
    print(f"📡 URL principale   : http://localhost:{PORT}")
    print(f"📁 Dossier média    : {os.path.abspath(MEDIA_FOLDER)}")
    print(f"📄 Fichier info     : {os.path.abspath(INFO_FILE)}")
    print(f"🔌 API Liste médias : http://localhost:{PORT}/api/media")
    print(f"📤 API Upload média : http://localhost:{PORT}/api/media/upload")
    print(f"🔔 API Alertes info : http://localhost:{PORT}/api/info")
    print(f"📢 API Ajout alerte : http://localhost:{PORT}/api/info/add")
    print("=" * 70)
    print("\n🔗 Accès rapide :")
    print(f"   • Page d'accueil : http://localhost:{PORT}/index.html?token=ADMIN001")
    print(f"   • Infos invités  : http://localhost:{PORT}/info.html")
    print(f"   • Admin infos    : http://localhost:{PORT}/info_admin.html")
    print(f"   • Galerie invités: http://localhost:{PORT}/media.html")
    print(f"   • Admin médias   : http://localhost:{PORT}/media_admin.html")
    print("\n⏹️  Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        httpd.shutdown()


if __name__ == '__main__':
    run_server()