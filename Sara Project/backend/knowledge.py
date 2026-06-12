from difflib import SequenceMatcher

knowledge_base = {
    'onboarding': {
        'keywords': ['onboarding', 'orientasi', 'pengenalan', 'baru', 'join', 'mulai kerja', 'karyawan baru', 'new hire'],
        'answer': 'Onboarding adalah proses pengenalan karyawan baru. Durasi 1-2 minggu dengan tahapan:\n1. Orientation umum (perkenalan perusahaan)\n2. Training departemen sesuai bidang\n3. Mentoring dengan senior\n4. Perkenalan dengan tim kerja\n\nPersiapkan KTP, NPWP, ijazah, dan pas foto 3x4.'
    },
    'jam_kerja': {
        'keywords': ['jam kerja', 'jam kantor', 'jam masuk', 'jam pulang', 'working hours', 'jam operasional', 'shift', 'waktu kerja'],
        'answer': 'Jam kerja PT Samaratu Daya Teknik:\n📅 Senin-Jumat: 08:00 - 17:00 WIB\n🍽️ Istirahat: 12:00 - 13:00\n📅 Sabtu-Minggu: LIBUR'
    },
    'benefit': {
        'keywords': ['benefit', 'tunjangan', 'asuransi', 'bonus', 'insentif', 'keuntungan', 'fasilitas karyawan', 'welfare'],
        'answer': 'Benefit karyawan PT Samaratu Daya Teknik:\n✅ Gaji kompetitif sesuai skill\n✅ Asuransi kesehatan (BPJS Kesehatan & Ketenagakerjaan)\n✅ THR dan bonus kinerja\n✅ Cuti tahunan 12 hari\n✅ Tunjangan makan & transport\n✅ Program training & pengembangan'
    },
    'gaji': {
        'keywords': ['gaji', 'salary', 'upah', 'bayaran', 'penghasilan', 'kompen', 'take home pay'],
        'answer': 'Gaji ditentukan berdasarkan level posisi, pengalaman, skill teknis, hasil interview, dan performa kerja.\n\nUntuk detail spesifik, hubungi HR:\n📧 hr@samaratu.com\n📞 (021) 1234-5678'
    },
    'cuti': {
        'keywords': ['cuti', 'libur', 'izin', 'leave', 'hari raya', 'cuti sakit', 'cuti tahunan', 'izin tidak masuk'],
        'answer': 'Kebijakan Cuti PT Samaratu Daya Teknik:\n🌴 Cuti tahunan: 12 hari per tahun\n🇮🇩 Cuti bersama: sesuai hari libur nasional\n🏥 Cuti sakit: sesuai surat dokter\n💍 Cuti khusus (nikah, keluarga meninggal): max 3 hari\n\n⚠️ Ajukan minimal 2 minggu sebelumnya via sistem HR.'
    },
    'lokasi': {
        'keywords': ['lokasi', 'alamat', 'tempat', 'kantor', 'office address', 'dimana', 'di mana', 'letak', 'maps', 'peta', 'jalan'],
        'type': 'location',
        'answer': '📍 Lokasi Kantor PT Samaratu Daya Teknik',
        'address': 'Jl. Pelita - Cipatuguran, Citarik, Kec. Pelabuhanratu, Kabupaten Sukabumi, Jawa Barat',
        'maps_url': 'https://maps.app.goo.gl/ozR4MYUVZZUG3A7h9',
        'details': 'Kantor berada di area strategis dekat jalan utama. Parkir tersedia untuk karyawan. Akses mudah dari arah Sukabumi dan Pelabuhan Ratu.'
    },
    'hr_contact': {
        'keywords': ['hr', 'human resource', 'contact hr', 'hubungi hr', 'kontak', 'telepon', 'email', 'cs', 'customer service'],
        'answer': 'Kontak HR PT Samaratu Daya Teknik:\n👤 HR Manager: Ibu Eka Putri Sari\n📧 Email: hr@samaratu.com\n📞 Phone: (021) 1234-5678\n💬 WhatsApp: +62-821-9999-8888\n🕐 Jam kerja: Senin-Jumat 08:00-17:00 WIB'
    },
    'departemen': {
        'keywords': ['departemen', 'divisi', 'bagian', 'team', 'struktur', 'organisasi', 'direktur', 'kepala', 'jabatan'],
        'answer': 'Struktur Departemen PT Samaratu Daya Teknik:\n1️⃣ TEKNIKAL - Engineering & Development\n   Kepala: Bapak Dede Efendi\n2️⃣ OPERASIONAL - Produksi & QA\n   Kepala: Bapak Hendro Wibowo\n3️⃣ PENJUALAN - Sales & Customer Service\n   Kepala: Ibu Dwi Kartika Namun\n4️⃣ HR & ADMIN - SDM & Administrasi\n   Manager: Ibu Eka Putri Sari\n5️⃣ FINANCE - Akuntansi & Keuangan'
    },
    'training': {
        'keywords': ['training', 'pelatihan', 'pembelajaran', 'development', 'course', 'belajar', 'kursus', 'sertifikasi'],
        'answer': 'Program Training & Development:\n1️⃣ Onboarding Training (1 minggu pertama)\n2️⃣ Technical Training sesuai bidang pekerjaan\n3️⃣ Soft Skill Training (komunikasi, leadership, time management)\n4️⃣ Sertifikasi Profesional (biaya ditanggung perusahaan)\n5️⃣ Mentoring Program dengan senior\n\n💡 Diskusikan rencana pengembanganmu dengan atasan atau HR.'
    },
    'lembur': {
        'keywords': ['lembur', 'overtime', 'kerja malam', 'shift malam', 'jam tambahan', 'ot'],
        'answer': 'Kebijakan Lembur:\n⏰ Jam 1: 1.5x gaji per jam\n⏰ Jam 2+: 2x gaji per jam\n🌙 Lembur malam (22:00-06:00): extra 25%\n\n⚠️ Memerlukan approval atasan terlebih dahulu dan pencatatan di sistem absensi.'
    },
    'dress_code': {
        'keywords': ['dress code', 'pakaian', 'seragam', 'baju', 'uniform', 'tampilan', 'busana'],
        'answer': 'Dress Code PT Samaratu Daya Teknik:\n👔 Senin-Kamis: Business Casual\n   (kemeja, celana panjang, sepatu rapi)\n👕 Jumat: Smart Casual\n\n🚫 Dilarang: Kaos oblong tanpa kerah\n   - Celana pendek\n   - Sandal jepit\n   - Pakaian ketat/terbuka'
    },
    'fasilitas': {
        'keywords': ['fasilitas', 'kantin', 'mushola', 'gym', 'parkir', 'rest area', 'sarana', 'toilet'],
        'answer': 'Fasilitas Kantor:\n🍽️ Kantin dengan subsidi\n🕌 Mushola\n🏋️ Gym (gratis untuk karyawan)\n🚗 Parkir gratis & aman 24 jam\n🔌 Rest Area dengan charging station\n📶 WiFi kantor\n\nTanya receptionist untuk akses detail fasilitas.'
    },
    'absensi': {
        'keywords': ['absensi', 'kehadiran', 'presensi', 'checkin', 'terlambat', 'attendance', 'finger', 'sidik jari'],
        'answer': 'Sistem Absensi:\n🔐 Biometric fingerprint atau aplikasi mobile\n⏰ Absen sebelum jam 08:00\n\nToleransi keterlambatan:\n🟢 1-15 menit: tidak ada potongan\n🟡 16-30 menit: potongan 0.25 hari\n🔴 >30 menit: potongan 0.5 hari'
    },
    'payroll': {
        'keywords': ['payroll', 'slip gaji', 'potongan', 'pajak', 'pph', 'gajian', 'tunjangan gaji', 'gaji bulanan'],
        'answer': 'Sistem Payroll:\n📅 Tanggal Gaji: Tanggal 25 setiap bulan\n📊 Komponen: Gaji pokok + tunjangan + bonus - PPh 21 - BPJS\n📄 Slip gaji bisa dilihat di portal karyawan atau print di HR'
    },
    'kesehatan': {
        'keywords': ['kesehatan', 'sehat', 'sakit', 'dokter', 'medical', 'k3', 'keselamatan kerja', 'bpjs', 'rumah sakit'],
        'answer': 'Program Kesehatan & Keselamatan:\n🏥 Asuransi kesehatan (BPJS + asuransi tambahan)\n🩺 Medical check-up gratis 1x per tahun\n🦺 K3: Briefing safety, APD wajib, lapor kecelakaan\n💊 Klinik & apotek di kantor\n\n⚠️ Sementara kecelakaan kerja? Segera lapor atasan dan HR!'
    },
    'evaluasi': {
        'keywords': ['evaluasi', 'penilaian', 'review', 'performa', 'performance', 'kinerja', 'appraisal'],
        'answer': 'Evaluasi Kinerja:\n📅 Jadwal: 3 bulan (trial), 6 bulan (permanent), tahunan (review)\n📋 Kriteria: Kualitas pekerjaan, produktivitas, kedisiplinan, teamwork, kemampuan belajar\n🏆 Hasil: Kenaikan gaji, promosi, program pengembangan'
    },
    'promosi': {
        'keywords': ['promosi', 'naik jabatan', 'karir', 'career', 'kenaikan pangkat', 'advance', 'jenjang'],
        'answer': 'Jalur Karir & Promosi:\n📋 Persyaratan:Minimal 1 tahun di posisi saat ini\n   - Evaluasi minimal "Baik"\n   - Rekomendasi atasan\n\n🚀 Jalur Karir:Teknis: Junior → Senior → Lead → Principal\n   - Managerial: Supervisor → Manager → Head → Director\n\n📝 Proses: Diskusi atasan → Submit HR → Assessment & interview → Keputusan'
    },
    'resign': {
        'keywords': ['resign', 'berhenti', 'keluar', 'pengunduran diri', 'quit', 'berhenti kerja', 'phk'],
        'answer': 'Proses Resign / Pengunduran Diri:\n📅 Notice Period: Minimal 1 bulan sebelumnya\n\n📋 Langkah-langkah:1. Diskusi dengan atasan langsung\n2. Buat surat resign resmi\n3. Submit ke HR\n4. Handover pekerjaan\n5. Exit interview\n6. Serah terima aset perusahaan\n\n💰 Settlement: Gaji akhir + bonus + uang cuti belum digunakan'
    },
    'salam': {
        'keywords': ['halo', 'hi', 'hello', 'apa kabar', 'pagi', 'sore', 'malam', 'hai', 'assalamualaikum', 'selamat'],
        'answer': 'Halo! 👋\n\nSaya SARA, Asisten Digital untuk PT Samaratu Daya Teknik.\nSaya siap membantu kamu dengan informasi tentang:\n• Onboarding & prosedur karyawan baru\n• Jam kerja, benefit, dan tunjangan\n• Cuti, lembur, dan absensi\n• Lokasi kantor dan fasilitas\n• Kontak HR dan departemen\n• Dan banyak lagi!\n\nAda yang bisa saya bantu? 😊'
    },
    'terima_kasih': {
        'keywords': ['terima kasih', 'thanks', 'makasih', 'thx', 'thank you', 'terimakasih'],
        'answer': 'Sama-sama! 😊 Senang bisa membantu.\n\nJika ada pertanyaan lagi, jangan ragu untuk bertanya. Semoga harimu menyenangkan dan produktif!'
    },
    'perusahaan': {
        'keywords': ['perusahaan', 'tentang', 'profil', 'visi', 'misi', 'sejarah', 'samaratu', 'sdt'],
        'answer': 'PT Samaratu Daya Teknik adalah perusahaan yang bergerak di bidang teknik dan teknologi.\n\nKami berkomitmen untuk memberikan solusi teknik berkualitas dengan tim profesional yang solid.\n\nUntuk informasi lebih detail tentang profil perusahaan, silakan hubungi HR atau kunjungi website resmi kami.'
    },
    'kontrak': {
        'keywords': ['kontrak', 'pkwt', 'pkwtt', 'perjanjian kerja', 'masa percobaan', 'probation'],
        'answer': 'Kebijakan Kontrak Kerja:\n📄 PKWT (Kontrak): Masa kerja tertentu, bisa diperpanjang\n📄 PKWTT (Tetap): Setelah memenuhi syarat\n\n⏳ Masa Percobaan (Probation): 3 bulan\n   - Evaluasi di akhir bulan ke-3\n   - Jika lolos, naik status menjadi karyawan tetap\n   - Gaji tetap diterima selama probation'
    }
}


def find_answer(user_message):
    """
    Cari jawaban dengan fuzzy matching yang lebih baik
    """
    msg = user_message.lower().strip()
    best_match = None
    best_score = 0.55  # threshold minimum 55% similarity

    for key, item in knowledge_base.items():
        for keyword in item['keywords']:
            # Exact match (prioritas tinggi)
            if keyword.lower() in msg:
                return item

            # Fuzzy matching untuk pertanyaan serupa
            similarity = SequenceMatcher(None, keyword.lower(), msg).ratio()
            if similarity > best_score:
                best_score = similarity
                best_match = item

    return best_match
