#!/usr/bin/env python3
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store')
        SimpleHTTPRequestHandler.end_headers(self)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/api/media':
            self.list_media()
            return
        if path == '/api/info':
            self.list_info()
            return
        if path == '/api/commentaires':
            self.list_commentaires()
            return
        
        SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        path = urlparse(self.path).path
        print(f"📨 POST: {path}")
        
        if path == '/api/media/upload':
            self.upload_media()
            return
        if path == '/api/info/add':
            self.add_info()
            return
        if path == '/api/invite/register':
            self.register_invite()
            return
        if path == '/api/commentaires/add':
            self.add_commentaire()
            return
        
        self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        path = urlparse(self.path).path
        
        if path.startswith('/api/media/'):
            self.delete_media(path.split('/')[-1])
            return
        if path.startswith('/api/info/'):
            self.delete_info(path.split('/')[-1])
            return
        if path.startswith('/api/commentaires/'):
            self.delete_commentaire(path.split('/')[-1])
            return
        
        self.send_error(404, "Not Found")
    
    def list_media(self):
        try:
            if not os.path.exists(MEDIA_FOLDER):
                os.makedirs(MEDIA_FOLDER)
            
            media_list = []
            for filename in os.listdir(MEDIA_FOLDER):
                filepath = os.path.join(MEDIA_FOLDER, filename)
                if os.path.isdir(filepath) or filename.startswith('.'):
                    continue
                
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                    media_type = 'image'
                elif ext in ['.mp4', '.webm', '.mov', '.avi']:
                    media_type = 'video'
                else:
                    continue
                
                media_list.append({
                    'filename': filename,
                    'type': media_type,
                    'timestamp': int(os.path.getmtime(filepath) * 1000),
                    'url': f'{MEDIA_FOLDER}/{filename}'
                })
            
            media_list.sort(key=lambda x: x['timestamp'], reverse=True)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'media': media_list}).encode('utf-8'))
        except Exception as e:
            print(f"❌ {e}")
            self.send_error(500, str(e))
    
    def upload_media(self):
        try:
            if not os.path.exists(MEDIA_FOLDER):
                os.makedirs(MEDIA_FOLDER)
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, 
                                  environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers.get('Content-Type')})
            if 'file' not in form:
                self.send_error(400, "Pas de fichier")
                return
            
            file_item = form['file']
            filename = os.path.basename(file_item.filename)
            filepath = os.path.join(MEDIA_FOLDER, filename)
            
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filename = f"{base}_{counter}{ext}"
                    filepath = os.path.join(MEDIA_FOLDER, filename)
                    counter += 1
            
            with open(filepath, 'wb') as f:
                f.write(file_item.file.read())
            
            print(f"✅ Upload: {filename}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'filename': filename}).encode('utf-8'))
        except Exception as e:
            print(f"❌ {e}")
            self.send_error(500, str(e))
    
    def delete_media(self, filename):
        try:
            filepath = os.path.join(MEDIA_FOLDER, os.path.basename(filename))
            os.remove(filepath)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def list_info(self):
        try:
            if not os.path.exists(INFO_FILE):
                with open(INFO_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'alerts': []}, f)
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def add_info(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            message = data.get('message', '').strip()
            
            if not os.path.exists(INFO_FILE):
                with open(INFO_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'alerts': []}, f)
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            import time
            new_alert = {'id': int(time.time() * 1000), 'message': message, 'timestamp': int(time.time() * 1000)}
            file_data.get('alerts', []).insert(0, new_alert)
            
            with open(INFO_FILE, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'alert': new_alert}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(f"❌ {e}")
            self.send_error(500, str(e))
    
    def delete_info(self, alert_id):
        try:
            with open(INFO_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['alerts'] = [a for a in data.get('alerts', []) if a['id'] != int(alert_id)]
            with open(INFO_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def register_invite(self):
        try:
            print("👤 Enregistrement")
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            nom = data.get('nom', '').strip()
            email = data.get('email', '').strip()
            print(f"   {nom} / {email}")
            
            if not os.path.exists(INVITE_FILE):
                with open(INVITE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'invites': []}, f)
            
            with open(INVITE_FILE, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            invites = file_data.get('invites', [])
            existing = next((i for i in invites if i['email'] == email), None)
            
            if existing:
                invite = existing
            else:
                import time
                invite = {'id': int(time.time() * 1000), 'nom': nom, 'email': email, 'timestamp': int(time.time() * 1000)}
                invites.append(invite)
                with open(INVITE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'invites': invites}, f, indent=2, ensure_ascii=False)
            
            print(f"✅ OK")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'invite': invite}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(f"❌ {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
    
    def list_commentaires(self):
        try:
            if not os.path.exists(COMMENTAIRE_FILE):
                with open(COMMENTAIRE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'commentaires': []}, f)
            with open(COMMENTAIRE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def add_commentaire(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if not os.path.exists(COMMENTAIRE_FILE):
                with open(COMMENTAIRE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'commentaires': []}, f)
            with open(COMMENTAIRE_FILE, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            import time
            new_comment = {'id': int(time.time() * 1000), 'nom': data['nom'], 'message': data['message'], 'timestamp': int(time.time() * 1000)}
            file_data.get('commentaires', []).append(new_comment)
            
            with open(COMMENTAIRE_FILE, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Commentaire")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'commentaire': new_comment}, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(f"❌ {e}")
            self.send_error(500, str(e))
    
    def delete_commentaire(self, comment_id):
        try:
            with open(COMMENTAIRE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['commentaires'] = [c for c in data.get('commentaires', []) if c['id'] != int(comment_id)]
            with open(COMMENTAIRE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))


if __name__ == '__main__':
    for f, d in [(INFO_FILE, {'alerts': []}), (INVITE_FILE, {'invites': []}), (COMMENTAIRE_FILE, {'commentaires': []})]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(d, file)
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
    
    print("🎉 Serveur Mariage - http://localhost:8000")
    server = HTTPServer(('', PORT), WeddingHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋")
        server.shutdown()