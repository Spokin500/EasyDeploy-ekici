from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)

# Eklentilerin tutulacağı klasör
UPLOAD_FOLDER = 'eklentiler'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ana sayfa (Senin istediğin mesaj)
@app.route('/')
def index():
    return "EasyDeploy Eklenti hizmetleri çalışıyor"

# Eklenti Yükleme Noktası (POST isteği atılır)
@app.route('/upload', methods=['POST'])
def upload_plugin():
    if 'file' not in request.files:
        return jsonify({"hata": "Dosya bulunamadı"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"hata": "Dosya seçilmedi"}), 400

    # Dosyayı sunucuya kaydet
    dosya_yolu = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(dosya_yolu)
    return jsonify({"mesaj": f"{file.filename} başarıyla eklendi!"}), 200

# Eklenti Çekme Noktası (GET isteği atılır)
@app.route('/download/<filename>', methods=['GET'])
def download_plugin(filename):
    dosya_yolu = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(dosya_yolu):
        # Dosya varsa karşı tarafa indirt
        return send_file(dosya_yolu, as_attachment=True)
    else:
        return jsonify({"hata": "Eklenti bulunamadı"}), 404

if __name__ == '__main__':
    # Render'ın atadığı portu al, yoksa 5000 kullan
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
