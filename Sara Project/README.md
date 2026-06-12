# 🤖 SARA - PT Samaratu Daya Teknik Chatbot

AI Chatbot untuk membantu karyawan dengan informasi perusahaan, onboarding, benefit, jam kerja, dan lainnya.

---

## 📁 Struktur Project

```
sara-bot/
├── app.py              # Backend Flask (Python)
├── knowledge.py        # Knowledge Base perusahaan
├── index.html          # Frontend Chat UI
├── style.css           # Styling
├── script.js           # Frontend Logic
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image untuk Railway
├── railway.json        # Railway deployment config
├── .dockerignore       # File yang di-exclude dari Docker
└── .env.example        # Template environment variables
```

---

## 🚀 Cara Menjalankan (Local Development)

### Opsi A: Tanpa Ollama (Pakai Groq API - Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Buat file `.env`:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` - isi GROQ_API_KEY:**
   ```
   GROQ_ENABLED=true
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
   OLLAMA_ENABLED=false
   ```

4. **Jalankan server:**
   ```bash
   python app.py
   ```

5. **Buka browser:** http://localhost:5000

---

### Opsi B: Dengan Ollama (Local LLM)

1. **Install Ollama:** https://ollama.com/download

2. **Download model:**
   ```bash
   ollama pull llama3
   ```

3. **Jalankan Ollama:**
   ```bash
   ollama serve
   ```

4. **Edit `.env`:**
   ```
   OLLAMA_ENABLED=true
   GROQ_ENABLED=false
   ```

5. **Jalankan Flask:**
   ```bash
   python app.py
   ```

---

## 🚂 Deploy ke Railway

### Langkah 1: Daftar Groq API (GRATIS)

1. Buka https://console.groq.com/keys
2. Login dengan Google/GitHub
3. Klik **"Create API Key"**
4. Copy API key-nya

### Langkah 2: Setup Railway

1. Buka https://railway.app dan login dengan GitHub
2. Klik **"New Project"** → **"Deploy from GitHub repo"**
3. Pilih repository project kamu
4. Klik **"Add Variables"** dan tambahkan:
   ```
   GROQ_ENABLED = true
   GROQ_API_KEY = gsk_xxxxxxxxxxxxxxxxxxxx  (paste dari Groq)
   OLLAMA_ENABLED = false
   FLASK_ENV = production
   ```
5. Railway akan otomatis build dan deploy!

### Langkah 3: Dapatkan URL

- Setelah deploy sukses, Railway akan kasih URL publik
- Contoh: `https://sara-bot.up.railway.app`
- Buka URL tersebut di browser → Chatbot siap digunakan!

---

## 🧠 Cara Kerja Bot

```
User bertanya
    ↓
Cek Knowledge Base (find_answer)
    ↓
Jika cocok → Jawab dari KB (cepat, akurat)
    ↓
Jika tidak cocok → Groq API / Ollama (AI generate)
    ↓
Tampilkan jawaban ke user
```

**Keunggulan:**
- ✅ Pertanyaan umum (jam kerja, benefit, cuti) → jawaban instan dari KB
- ✅ Pertanyaan kompleks/unik → dijawab AI (Groq/Ollama)
- ✅ Location response dengan Google Maps button
- ✅ Fallback message jika semua sumber gagal

---

## 📝 Menambah Knowledge Base

Edit file `knowledge.py` dan tambahkan entry baru:

```python
'kategori_baru': {
    'keywords': ['kata kunci', 'sinonim', 'lainnya'],
    'answer': 'Jawaban yang ingin ditampilkan'
}
```

Contoh:
```python
'wifi': {
    'keywords': ['wifi', 'internet', 'password wifi', 'jaringan'],
    'answer': 'Password WiFi kantor: Samaratu2024!\nSSID: SDT-Office'
}
```

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `Module not found` | `pip install -r requirements.txt` |
| `Port already in use` | Ganti port: `PORT=5001 python app.py` |
| `Groq API error` | Cek API key di `.env` atau dashboard Groq |
| `Ollama timeout` | Pastikan Ollama running: `ollama serve` |
| `Static files not found` | Pastikan `index.html`, `style.css`, `script.js` di folder yang sama dengan `app.py` |
| Railway build fail | Cek `Dockerfile` dan `requirements.txt` ada di root repo |

---

## 🎓 Tips untuk Magang

1. **Knowledge Base adalah nilai plus** - Tunjukkan ke dosen/pembimbing bahwa kamu membuat sistem FAQ yang terstruktur, bukan cuma chatbot generik.

2. **Dokumentasi** - Screenshot hasil chatbot, jelaskan arsitektur (KB + LLM hybrid), dan tunjukkan deployment berhasil.

3. **Tambah fitur** - Kamu bisa tambahkan:
   - Upload PDF untuk knowledge base otomatis
   - History chat per user
   - Admin panel untuk edit KB
   - Voice input/output

4. **Demo Groq** - Groq API gratis dan cepat, cocok untuk demo magang tanpa perlu setup server mahal.

---

## 🔒 Security Features

- ✅ Password hashing dengan Werkzeug
- ✅ Session management
- ✅ Input validation
- ✅ File upload security (whitelist extension)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Environment variables untuk secrets

## 📊 Architecture


## 📄 License

Project ini untuk keperluan akademik (magang).

---

**Dibuat dengan ❤️ untuk PT Samaratu Daya Teknik**
