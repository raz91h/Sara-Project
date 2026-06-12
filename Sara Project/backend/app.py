from dotenv import load_dotenv
load_dotenv()

from database import (
    init_db, get_user_by_username, get_user_by_id, create_user,
    create_submission, get_submissions, update_submission_status,
    create_announcement, get_announcements, create_rating, get_ratings,
    save_chat, get_chat_logs, get_dashboard_stats, update_user_credentials
)
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import requests, os, sys, json
from datetime import datetime
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from knowledge import find_answer
except ImportError:
    def find_answer(msg):
        return None

# ==================== INIT ====================
app = Flask(__name__, template_folder=BASE_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'sara_secret_key_2026_change_in_production')
app.config['SESSION_PERMANENT'] = True
CORS(app)
init_db()

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# ==================== CONFIG ====================
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_ENABLED = os.environ.get('GROQ_ENABLED', 'true').lower() == 'true'
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_ENABLED = os.environ.get('OLLAMA_ENABLED', 'true').lower() == 'true'
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3')

SYSTEM_PROMPT = """Kamu adalah SARA, Asisten Digital untuk PT Samaratu Daya Teknik. 
PRIORITAS: Berikan informasi akurat tentang perusahaan (onboarding, jam kerja, benefit, cuti, dll)
GAYA: Ramah, profesional, gunakan emoji yang sesuai."""

# ==================== MIDDLEWARE ====================
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized - Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized - Please login first'}), 401
        user = get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Forbidden - Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTH ROUTES ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Admin login route
    GET: Show login form
    POST: Process login credentials
    """
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Validate input
        if not username or not password:
            return render_template("login.html", error="Username dan password wajib diisi")
        
        print(f"\n{'='*60}")
        print(f"🔐 Login attempt: {username}")
        
        # Get user from database
        user = get_user_by_username(username)
        
        if user:
            print(f"👤 User found: {user['nama']} (Role: {user['role']})")
            # Simple plaintext comparison (TODO: implement hashing in production)
            if user['password'] == password:
                # Check if admin
                if user['role'] == 'admin':
                    # Create session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session.permanent = True
                    
                    print(f"✅ Login successful: {username} (ID: {user['id']})")
                    print(f"{'='*60}\n")
                    return redirect("/admin")
                else:
                    print(f"❌ Non-admin user tried to login as admin: {username}")
                    print(f"{'='*60}\n")
                    return render_template("login.html", error="Hanya admin yang bisa login")
            else:
                print(f"❌ Wrong password for user: {username}")
                print(f"{'='*60}\n")
                return render_template("login.html", error="Username atau Password salah")
        else:
            print(f"❌ User not found: {username}")
            print(f"{'='*60}\n")
            return render_template("login.html", error="Username atau Password salah")
    
    return render_template("login.html")

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.json
    try:
        create_user(data['nama'], data['username'], data['password'], 
                   data.get('email', ''), data.get('jabatan', ''), data.get('nip', ''))
        return jsonify({'success': True, 'message': 'Registrasi berhasil'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/logout')
def logout():
    """Logout and clear session"""
    username = session.get('username', 'unknown')
    session.clear()
    print(f"🔓 User logged out: {username}")
    return jsonify({'success': True})

@app.route('/api/user')
@login_required
def get_user():
    """Get current user info"""
    user = get_user_by_id(session['user_id'])
    return jsonify(user)

# ==================== ADMIN SETTINGS ====================
@app.route('/api/admin/change-credentials', methods=['POST'])
@admin_required
def change_admin_credentials():
    """Change admin username and/or password"""
    try:
        data = request.json
        user_id = session['user_id']
        current_password = data.get('current_password', '').strip()
        new_username = data.get('new_username', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Get current user
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User tidak ditemukan'}), 404
        
        # Verify current password
        if user['password'] != current_password:
            print(f"❌ Wrong current password for admin: {user['username']}")
            return jsonify({'error': 'Password saat ini salah'}), 401
        
        # Validate new password if provided
        if new_password:
            if len(new_password) < 6:
                return jsonify({'error': 'Password baru minimal 6 karakter'}), 400
            
            if new_password != confirm_password:
                return jsonify({'error': 'Konfirmasi password tidak sesuai'}), 400
        
        # Validate new username if provided
        if new_username and new_username != user['username']:
            if len(new_username) < 3:
                return jsonify({'error': 'Username minimal 3 karakter'}), 400
        
        # Check if at least one field is being updated
        if not new_username and not new_password:
            return jsonify({'error': 'Pilih username atau password untuk diubah'}), 400
        
        # Update credentials
        try:
            update_user_credentials(
                user_id,
                username=new_username if new_username and new_username != user['username'] else None,
                password=new_password if new_password else None
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
        print(f"✅ Admin credentials updated")
        print(f"   Old username: {user['username']}")
        if new_username and new_username != user['username']:
            print(f"   New username: {new_username}")
            # Update session
            session['username'] = new_username
        if new_password:
            print(f"   Password changed")
        
        return jsonify({
            'success': True, 
            'message': 'Kredensial berhasil diubah',
            'new_username': new_username if new_username else user['username']
        })
    
    except Exception as e:
        print(f"❌ Error changing credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== CHAT ROUTE ====================
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - NO AUTH NEEDED for users"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Pesan tidak boleh kosong'}), 400

        print(f"\n{'='*60}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 USER: {user_message}")

        # Check KB
        print("🔍 Checking Knowledge Base...")
        kb_result = find_answer(user_message)
        
        if kb_result:
            print("✅ FOUND IN KNOWLEDGE BASE")
            answer = kb_result.get('answer') if isinstance(kb_result, dict) else kb_result
            save_chat(None, user_message, str(answer), 'kb')
            
            if isinstance(kb_result, dict) and kb_result.get('type') == 'location':
                print(f"{'='*60}\n")
                return jsonify({
                    'reply': kb_result['answer'],
                    'type': 'location',
                    'address': kb_result.get('address'),
                    'maps_url': kb_result.get('maps_url'),
                    'details': kb_result.get('details'),
                    'source': 'kb'
                })
            
            print(f"📝 ANSWER: {str(answer)[:100]}...")
            print(f"{'='*60}\n")
            return jsonify({'reply': answer, 'source': 'kb'})

        # Try Groq
        if GROQ_ENABLED and GROQ_API_KEY:
            print("🤖 Using Groq API...")
            response = call_groq(user_message)
            if response:
                print(f"📝 GROQ ANSWER: {str(response)[:100]}...")
                print(f"{'='*60}\n")
                save_chat(None, user_message, response, 'groq')
                return jsonify({'reply': response, 'source': 'groq'})

        # Try Ollama
        if OLLAMA_ENABLED:
            print("🤖 Using Ollama...")
            response = call_ollama(user_message)
            if response:
                print(f"📝 OLLAMA ANSWER: {str(response)[:100]}...")
                print(f"{'='*60}\n")
                save_chat(None, user_message, response, 'ollama')
                return jsonify({'reply': response, 'source': 'ollama'})

        # Fallback
        print("⚠️  ALL LLM SOURCES FAILED")
        print(f"{'='*60}\n")
        fallback = 'Maaf, saya tidak bisa menjawab. Hubungi HR: hr@samaratu.com atau (021) 1234-5678'
        save_chat(None, user_message, fallback, 'fallback')
        return jsonify({'reply': fallback, 'source': 'fallback'})

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== SUBMISSION ROUTES ====================
@app.route('/api/submissions', methods=['POST'])
def create_pengajuan():
    """Create leave/submission request - NO AUTH NEEDED"""
    try:
        nama = request.form.get('nama', '').strip()
        nip = request.form.get('nip', '').strip()
        jenis = request.form.get('jenis')
        tanggal_mulai = request.form.get('tanggal_mulai')
        tanggal_selesai = request.form.get('tanggal_selesai')
        alasan = request.form.get('alasan', '')
        
        # Validate required fields
        if not nama or not nip or not jenis or not tanggal_mulai or not tanggal_selesai:
            return jsonify({'success': False, 'message': 'Semua field wajib diisi'}), 400
        
        lampiran = None
        if 'lampiran' in request.files:
            file = request.files['lampiran']
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in ALLOWED_EXTENSIONS:
                    filename = f"cuti_{nip}_{int(datetime.now().timestamp())}.{ext}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    lampiran = filename

        # User ID opsional untuk anonymous submission
        user_id = session.get('user_id') if 'user_id' in session else None
        create_submission(user_id, nama, nip, jenis, tanggal_mulai, tanggal_selesai, alasan, lampiran)
        print(f"✅ Leave submission created: {nama} ({jenis}) - NIP: {nip}")
        return jsonify({'success': True, 'message': 'Pengajuan berhasil dikirim'})
    except Exception as e:
        print(f"❌ Error creating submission: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/submissions', methods=['GET'])
@admin_required
def list_pengajuan():
    """Get all submissions (admin only)"""
    subs = get_submissions()
    return jsonify(subs)

@app.route('/api/submissions/<int:id>/status', methods=['PUT'])
@admin_required
def update_status(id):
    """Update submission status (admin only)"""
    data = request.json
    status = data.get('status')
    
    if status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Status tidak valid'}), 400
    
    update_submission_status(id, status)
    print(f"✅ Submission {id} status updated to: {status}")
    return jsonify({'message': f'Status diubah ke {status}'})

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
def admin():
    """Admin dashboard page"""
    # Check if user is logged in and is admin
    if 'user_id' not in session:
        print(f"⚠️  Unauthorized access to /admin - redirecting to login")
        return redirect("/login")
    
    user = get_user_by_id(session['user_id'])
    if not user or user['role'] != 'admin':
        print(f"⚠️  Non-admin user {session.get('username')} tried to access admin")
        return redirect("/login")
    
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/api/stats')
@admin_required
def stats():
    """Get dashboard statistics (admin only)"""
    try:
        data = get_dashboard_stats()
        print(f"📊 Stats retrieved for admin: {session.get('username')}")
        return jsonify(data)
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cuti')
@admin_required
def all_cuti():
    """Get all leave requests (admin only)"""
    try:
        subs = get_submissions()
        print(f"📋 Cuti list retrieved: {len(subs)} items")
        return jsonify(subs)
    except Exception as e:
        print(f"❌ Error getting cuti: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pengumuman', methods=['POST'])
@admin_required
def buat_pengumuman():
    """Create announcement (admin only)"""
    data = request.json
    try:
        judul = data.get('judul', '').strip()
        isi = data.get('isi', '').strip()
        tipe = data.get('tipe', 'info')
        
        if not judul or not isi:
            return jsonify({'error': 'Judul dan isi wajib diisi'}), 400
        
        create_announcement(judul, isi, tipe, session['user_id'])
        print(f"✅ Announcement created: '{judul}' by {session.get('username')}")
        return jsonify({'success': True, 'message': 'Pengumuman berhasil dibuat'})
    except Exception as e:
        print(f"❌ Error creating announcement: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/pengumuman', methods=['GET'])
def list_pengumuman():
    """Get all announcements (public - no auth needed)"""
    try:
        announcements = get_announcements()
        return jsonify(announcements)
    except Exception as e:
        print(f"❌ Error getting announcements: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    """Submit survey response - NO AUTH NEEDED"""
    data = request.json
    try:
        rating = data.get('rating')
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating harus antara 1-5'}), 400
        
        nama = data.get('nama', 'Anonim')
        saran = data.get('saran', '')
        
        # User ID opsional untuk anonymous feedback
        user_id = session.get('user_id') if 'user_id' in session else None
        create_rating(user_id, nama, rating, saran)
        print(f"⭐ Survey submitted: {rating} stars by {nama}")
        return jsonify({'message': 'Terima kasih atas feedback Anda!'})
    except Exception as e:
        print(f"❌ Error submitting survey: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/survey', methods=['GET'])
@admin_required
def list_survey():
    """Get all survey responses (admin only)"""
    try:
        ratings = get_ratings()
        print(f"⭐ Survey list retrieved: {len(ratings)} responses")
        return jsonify(ratings)
    except Exception as e:
        print(f"❌ Error getting survey: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-logs', methods=['GET'])
@admin_required
def get_logs():
    """Get chat logs (admin only)"""
    try:
        logs = get_chat_logs()
        print(f"💬 Chat logs retrieved: {len(logs)} logs")
        return jsonify(logs)
    except Exception as e:
        print(f"❌ Error getting chat logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== STATIC ====================
@app.route('/')
def index():
    """Home page"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory(BASE_DIR, filename)
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/test', methods=['GET'])
def test():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'SARA Server Running',
        'timestamp': datetime.now().isoformat(),
        'ollama_enabled': OLLAMA_ENABLED,
        'groq_enabled': GROQ_ENABLED and bool(GROQ_API_KEY)
    })

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    print(f"❌ Server error: {str(e)}")
    return jsonify({'error': 'Server error'}), 500

# ==================== LLM FUNCTIONS ====================
def call_groq(message):
    """Call Groq API for response"""
    try:
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': GROQ_MODEL,
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message}
            ],
            'temperature': 0.7,
            'max_tokens': 1024
        }
        response = requests.post('https://api.groq.com/openai/v1/chat/completions',
                                headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"❌ Groq error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Groq error: {str(e)}")
    return None

def call_ollama(message):
    """Call Ollama local LLM for response"""
    try:
        response = requests.post(OLLAMA_URL,
            json={
                'model': OLLAMA_MODEL,
                'prompt': f"{SYSTEM_PROMPT}\n\nUser: {message}\nAssistant:",
                'stream': False,
                'temperature': 0.7
            }, timeout=60)
        if response.status_code == 200:
            return response.json().get('response')
        else:
            print(f"❌ Ollama error {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama error: {str(e)}")
    return None

# ==================== MAIN ====================
if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 SARA BOT - PT SAMARATU DAYA TEKNIK')
    print('='*60)
    print(f'✅ Mode:     {"Groq + KB" if GROQ_ENABLED and GROQ_API_KEY else "Ollama + KB"}')
    print(f'📡 Ollama:   {"ENABLED" if OLLAMA_ENABLED else "DISABLED"}')
    print(f'🤖 Groq:     {"ENABLED" if GROQ_ENABLED and GROQ_API_KEY else "DISABLED"}')
    print(f'📁 KB:       Loaded')
    print(f'⏰ Started:  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*60)
    print('🌐 Server running at http://localhost:5000')
    print('⚙️  Admin at http://localhost:5000/admin')
    print('📝 Default admin - username: admin | password: admin123')
    print('='*60 + '\n')

    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
