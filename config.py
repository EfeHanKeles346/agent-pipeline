"""
Pipeline Konfigurasyonu
- Model seçimleri, retry sayıları, dosya yolları buradan yönetilir
- Her proje için bu dosyayı düzenleyebilirsin
"""

import os

# .env dosya desteği (opsiyonel — pip install python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================
# API KEY
# ============================================
# Yöntem 1: .env dosyası (önerilen) — proje root'una .env oluştur:
#   ANTHROPIC_API_KEY=sk-ant-xxxxx
#
# Yöntem 2: Environment variable:
#   export ANTHROPIC_API_KEY='sk-ant-xxxxx'
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ============================================
# MODEL SEÇİMLERİ
# ============================================
# Her agent için ayrı model seçebilirsin
# Seçenekler: "claude-sonnet-4-20250514", "claude-haiku-4-20250514", "claude-opus-4-20250514"

MODELS = {
    "planner":   "claude-sonnet-4-20250514",
    "coder":     "claude-sonnet-4-20250514",
    "reviewer":  "claude-sonnet-4-20250514",
    "tester":    "claude-haiku-4-20250514",     # Basit kontrol — Haiku yeterli
    "committer": "claude-haiku-4-20250514",     # Mesaj üretimi — Haiku yeterli
}

# ============================================
# PIPELINE AYARLARI
# ============================================

# Reviewer onaylamazsa kaç kere Coder'a geri dönülsün
MAX_REVIEW_ATTEMPTS = 3

# Tester ve Committer agent'larını aktif/pasif yap
ENABLE_TESTER = True
ENABLE_COMMITTER = False  # Git repo yokken gereksiz — repo oluşunca aktif et

# Task'lar arası bekleme süresi (saniye) — rate limit koruması
TASK_COOLDOWN_SECONDS = 5

# ============================================
# DOSYA YOLLARI
# ============================================

# Proje kök dizini (pipeline'ın kendisi)
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

# System prompt'ların bulunduğu klasör
PROMPTS_DIR = os.path.join(PIPELINE_DIR, "prompts")

# Workspace — hedef projenin olduğu yer
# Bunu her proje için değiştir!
WORKSPACE_DIR = os.path.join(PIPELINE_DIR, "workspace")

# Todolist ve memory dosyaları
TODOLIST_FILE = os.path.join(WORKSPACE_DIR, "todolist.md")
MEMORY_FILE = os.path.join(WORKSPACE_DIR, "memory.md")

# Log klasörü
LOGS_DIR = os.path.join(PIPELINE_DIR, "logs")

# ============================================
# OTOMASYON AYARLARI
# ============================================

# Task'lar tamamlanınca otomatik npm install / pip install çalıştır
AUTO_INSTALL = True

# Tüm task'lar bitince dev server'ı otomatik başlat
AUTO_DEV_SERVER = True

# Her task öncesi workspace dosyalarını Coder/Planner'a gönder
SEND_WORKSPACE_CONTEXT = True

# ============================================
# TOKEN LİMİTLERİ
# ============================================
MAX_TOKENS = 16384  # Her agent'ın max output token'ı

# ============================================
# CONTEXT LİMİTLERİ
# ============================================
MAX_WORKSPACE_CONTEXT_CHARS = 80000  # Workspace context toplam karakter limiti (~20K token)
MAX_FILE_SIZE = 10000                # Dosya başına max karakter
