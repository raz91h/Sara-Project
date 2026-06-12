from datetime import datetime
from typing import Dict, Tuple

def validate_cuti_submission(data: Dict) -> Tuple[bool, str]:
    """Validate leave request data"""
    
    # Check required fields
    required = ['nama', 'nip', 'jenis', 'tanggal_mulai', 'tanggal_selesai']
    for field in required:
        if not data.get(field):
            return False, f"Field '{field}' wajib diisi"
    
    # Validate dates
    try:
        mulai = datetime.strptime(data['tanggal_mulai'], '%Y-%m-%d')
        selesai = datetime.strptime(data['tanggal_selesai'], '%Y-%m-%d')
        
        if mulai > selesai:
            return False, "Tanggal mulai harus sebelum tanggal selesai"
        
        if mulai < datetime.now().date():
            return False, "Tanggal mulai tidak boleh di masa lalu"
            
    except ValueError:
        return False, "Format tanggal harus YYYY-MM-DD"
    
    return True, "Valid"

def validate_user_input(username: str, password: str) -> Tuple[bool, str]:
    """Validate login credentials"""
    
    if not username or len(username) < 3:
        return False, "Username minimal 3 karakter"
    
    if not password or len(password) < 6:
        return False, "Password minimal 6 karakter"
    
    return True, "Valid"