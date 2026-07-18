from flask import Flask, jsonify, request, send_file
import os
import json

app = Flask(__name__)

# --- 1. AYARLAR.TXT DOSYASINI OKUMA BÖLÜMÜ ---
ayarlar = {}

def ayarlari_yukle():
    try:
        with open("ayarlar.txt", "r", encoding="utf-8") as dosya:
            for satir in dosya:
                if ":" in satir:
                    anahtar, deger = satir.split(":", 1)
                    ayarlar[anahtar.strip()] = deger.strip()
    except FileNotFoundError:
        print("HATA: ayarlar.txt dosyası bulunamadı!")

ayarlari_yukle()

GIZLI_KEY = ayarlar.get("gizli_key")
DISCORD_TOKEN = ayarlar.get("token")
ISTEMCI_ID = ayarlar.get("istemci_id")
API_KEY = ayarlar.get("api_key", "VARSAYILAN_KEY_123") # Txt'den çeker, yoksa varsayılan kullanır

# Klasör ayarları
UPLOAD_FOLDER = 'eklentiler'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- 2. EKLENTİ NUMARALANDIRMA SİSTEMİ (KAYIT DEFTERİ) ---
REGISTRY_FILE = "eklenti_kayit.json"

def kayitlari_al():
    # Mevcut kayıtları JSON'dan oku
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    return {}

def kayit_ekle(dosya_adi):
    kayitlar = kayitlari_al()
    
    # Dosya zaten kayıtlıysa ID'sini geri ver
    for pid, name in kayitlar.items():
        if name == dosya_adi:
            return pid
            
    # Yeni dosya ise, yeni bir numara (ID) oluştur
    yeni_id = str(len(kayitlar) + 1)
    kayitlar[yeni_id] = dosya_adi
    
    # JSON dosyasına kaydet
    with open(REGISTRY_FILE, "w") as f:
        json.dump(kayitlar, f)
    return yeni_id

# --- 3. WEB SERVİSİ VE API ENDPOINT'LERİ ---

# Ana Sayfa: Site açılınca API Key'i ve bilgileri gösterir
@app.route('/')
def index():
    return f"""
    <h1>EasyDeploy Eklenti Hizmetleri Aktif</h1>
    <p>Sisteminizi bağlamak için aşağıdaki API Key'i kopyalayın:</p>
    <h2 style='color:blue;'>{API_KEY}</h2>
    """

# API 1: Sistemdeki tüm eklentileri numaralarıyla listeler
@app.route('/api/eklentiler', methods=['GET'])
def eklentileri_listele():
    # URL'den gelen ?key= parametresini kontrol et
    gelen_key = request.args.get('key')
    
    if gelen_key != API_KEY:
        return jsonify({"hata": "Yetkisiz Erişim! Geçersiz API Key."}), 403
        
    # Eklentiler klasörünü tara ve yeni .py/.zip dosyalarını numaralandır
    for dosya in os.listdir(UPLOAD_FOLDER):
        if dosya.endswith(".py") or dosya.endswith(".zip"):
            kayit_ekle(dosya)
            
    kayitlar = kayitlari_al()
    return jsonify({
        "mesaj": "API Key Doğrulandı",
        "toplam_eklenti": len(kayitlar),
        "eklentiler": kayitlar
    })

# API 2: Numaraya (ID) göre eklentiyi çeker/indirir
@app.route('/api/indir/<id>', methods=['GET'])
def eklenti_indir(id):
    gelen_key = request.args.get('key')
    
    if gelen_key != API_KEY:
        return jsonify({"hata": "Yetkisiz Erişim! Geçersiz API Key."}), 403
        
    kayitlar = kayitlari_al()
    dosya_adi = kayitlar.get(str(id))
    
    if not dosya_adi:
        return jsonify({"hata": f"Sistemde {id} numaralı eklenti bulunamadı!"}), 404
        
    dosya_yolu = os.path.join(UPLOAD_FOLDER, dosya_adi)
    
    if os.path.exists(dosya_yolu):
        return send_file(dosya_yolu, as_attachment=True)
    else:
        return jsonify({"hata": "Eklenti kayıtlı ama dosyası sunucudan silinmiş!"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
