# Multi-Agent Pipeline — Kapsamlı İyileştirme Raporu v2

**Tarih:** 2026-03-30
**Kapsam:** Pipeline kodu, agent'lar, prompt'lar, tools, config — tüm proje
**Mevcut Durum:** v1 iyileştirmeleri uygulandı (retry, DRY, prompt hardening, context limit vb.)
**Projenin Doğası:** Bu pipeline bir **genel amaçlı proje oluşturucudur.** Workspace'e farklı `memory.md` ve `todolist.md` koyarak React, Python, C++, Go, Rust — herhangi bir dilde proje üretebilir. Pipeline kodu hiçbir dile/framework'e bağlı OLMAMALIDIR.
**Hedef:** Bu dokümanı okuyan bir AI agent, adımları sırayla uygulayarak projeyi production-ready seviyeye getirebilmeli.

---

## OKUMA KILAVUZU

Bu doküman bir **uygulama kılavuzudur**. Okuyan agent (veya geliştirici) şu sırayı takip etmelidir:

1. Önce **Bölüm 1**'i oku → Projenin mevcut durumunu ve felsefesini anla
2. Sonra **Bölüm 2**'yi oku → Tespit edilen sorunların kök nedenlerini anla
3. **Bölüm 3-8**'i sırayla uygula → Her faz önceki fazın tamamlanmış olmasını gerektirir
4. Her adımdan sonra **Doğrulama** bölümünü çalıştır → Adımın doğru uygulandığını teyit et
5. Tüm fazlar bitince **Bölüm 9**'daki Final Checklist'i çalıştır

**Kurallar:**
- Adımları SIRASIZ uygulama — bağımlılıklar var
- Her adımda sadece belirtilen dosyaları değiştir
- Bir adımı uyguladıktan sonra proje ÇALIŞIR durumda kalmalı
- Doğrulama başarısız olursa, o adımı düzelt, sonraki adıma geçme
- **HİÇBİR değişiklik belirli bir dile veya framework'e bağlı olmamalı.** Pipeline C++ projesi de, Python Flask API'si de, React SPA'sı da üretebilmeli.

---

## İÇİNDEKİLER

1. [Mevcut Durum Analizi](#1-mevcut-durum-analizi)
2. [Tespit Edilen Sorunlar ve Kök Nedenler](#2-tespit-edilen-sorunlar-ve-kök-nedenler)
3. [Faz 1 — Proje Altyapısı (Git, README, Test Altyapısı)](#3-faz-1--proje-altyapısı)
4. [Faz 2 — Dil-Agnostik Pipeline (Çoklu Dil/Platform Desteği)](#4-faz-2--dil-agnostik-pipeline)
5. [Faz 3 — Pipeline Mantık Hataları](#5-faz-3--pipeline-mantık-hataları)
6. [Faz 4 — Agent Kalitesi ve Prompt Mühendisliği](#6-faz-4--agent-kalitesi-ve-prompt-mühendisliği)
7. [Faz 5 — Token Ekonomisi ve Maliyet Optimizasyonu](#7-faz-5--token-ekonomisi-ve-maliyet-optimizasyonu)
8. [Faz 6 — Yeni Yetenekler](#8-faz-6--yeni-yetenekler)
9. [Final Checklist ve Kabul Kriterleri](#9-final-checklist-ve-kabul-kriterleri)

---

## 1. Mevcut Durum Analizi

### 1.1 Pipeline Felsefesi

Bu pipeline bir **genel amaçlı AI project builder**'dır:

```
KULLANICI                          PIPELINE                         ÇIKTI
─────────                          ────────                         ─────
memory.md (proje tanımı)    →   Planner → Coder ⇄ Reviewer   →   Çalışır proje
todolist.md (görev listesi) →   → Tester → (Build Test)       →   workspace/ içinde
```

**Kullanım senaryoları:**
- `memory.md`'ye "React portfolio sitesi" yaz → React/TypeScript projesi üretir
- `memory.md`'ye "Python CLI tool" yaz → Python projesi üretir
- `memory.md`'ye "C++ ray tracer" yaz → C++ projesi üretir
- `memory.md`'ye "Go REST API" yaz → Go projesi üretir
- Workspace'i temizle, yeni `memory.md` ve `todolist.md` koy → bambaşka bir proje

Bu demek oluyor ki pipeline'ın kendisi **hiçbir dile/framework'e bağlı OLMAMALI**.

### 1.2 Proje Yapısı

```
agent-pipeline/
├── agents/                    # AI agent sınıfları
│   ├── __init__.py            # Export'lar
│   ├── base.py                # BaseAgent (retry, JSON parse, token tracking)
│   ├── planner.py             # Plan üretir
│   ├── coder.py               # Kod yazar / düzeltir
│   ├── reviewer.py            # Kod review eder
│   ├── tester.py              # Statik analiz yapar
│   └── committer.py           # Commit mesajı üretir (devre dışı)
├── tools/
│   ├── __init__.py            # Boş (sorunlu — export yok)
│   ├── file_tools.py          # Dosya I/O, state, memory, workspace okuma
│   └── shell_tools.py         # Shell komutları, dev server
├── prompts/                   # Agent system prompt'ları (markdown)
│   ├── planner.md
│   ├── coder.md
│   ├── reviewer.md
│   ├── tester.md
│   └── committer.md
├── workspace/                 # Hedef proje (DEĞİŞKEN — herhangi bir dilde olabilir)
├── logs/                      # Task execution log'ları
├── config.py                  # Merkezi konfigürasyon
├── main.py                    # Pipeline orchestrator
├── requirements.txt           # Python bağımlılıkları
├── .gitignore                 # Git ignore kuralları
├── .env.example               # API key şablonu
└── improvements.md            # Bu dosya
```

### 1.3 v1 İyileştirmeleri (Daha Önce Uygulandı)

| İyileştirme | Durum |
|---|---|
| API key hardcoded kaldırıldı, .env desteği | Uygulandı |
| .gitignore oluşturuldu | Uygulandı |
| Exponential backoff retry (3 deneme, 5s→10s→20s) | Uygulandı |
| Tester'a existing_files gönderimi | Uygulandı |
| Tester prompt yeniden yazıldı | Uygulandı |
| Task arası cooldown (5s) | Uygulandı |
| Reviewer prompt sertleştirildi (skor enflasyonu kontrolü) | Uygulandı |
| Coder prompt'a "mevcut kodu bozma yasağı" eklendi | Uygulandı |
| Planner prompt'a token yönetimi eklendi | Uygulandı |
| Committer devre dışı bırakıldı | Uygulandı |
| JSON parse DRY refactoring (run_json) | Uygulandı |
| Context karakter limiti (80K) | Uygulandı |
| Akıllı model seçimi (Haiku for tester/committer) | Uygulandı |
| save_code_files satır-satır parser | Uygulandı |
| Pipeline state persistence (save/load/clear) | Uygulandı |
| Gerçek build test (npm run build) | Uygulandı |
| Memory.md otomatik güncelleme | Uygulandı |

### 1.4 Kalan Sorunlar Özeti

| # | Sorun | Önem | Kategori |
|---|---|---|---|
| 1 | Pipeline sadece Node ve Python tanıyor (C++, Go, Rust, Java yok) | KRİTİK | Dil desteği |
| 2 | Tester prompt'u React/TypeScript'e özgü yazılmış | KRİTİK | Dil desteği |
| 3 | Build test sadece `npm run build` çalıştırıyor | KRİTİK | Dil desteği |
| 4 | `TEXT_EXTENSIONS` C/C++, Go, Rust, Java dosyalarını tanımıyor | YÜKSEK | Dil desteği |
| 5 | `IGNORED_DIRS` C++/Rust build dizinlerini tanımıyor | YÜKSEK | Dil desteği |
| 6 | Config dosyası önceliklendirmesi sadece web projelerine bakıyor | YÜKSEK | Dil desteği |
| 7 | Git repo yok — versiyon kontrolü sıfır | KRİTİK | Altyapı |
| 8 | README.md yok | YÜKSEK | Altyapı |
| 9 | Unit test sıfır | YÜKSEK | Güvenilirlik |
| 10 | State recovery adım-bazlı çalışmıyor | YÜKSEK | Mantık |
| 11 | Build failure Coder'a geri beslenmiyor | YÜKSEK | Mantık |
| 12 | Token tracking pipeline seviyesinde toplanmıyor | ORTA | Maliyet |
| 13 | Memory.md sınırsız büyüyor | ORTA | Bakım |
| 14 | --verbose flag yok | ORTA | UX |
| 15 | Workspace temizleme/sıfırlama komutu yok | ORTA | UX |

---

## 2. Tespit Edilen Sorunlar ve Kök Nedenler

### 2.1 KRİTİK: Pipeline Dil-Bağımlı Yazılmış

**Sorunun kapsamı:** Pipeline'ın 4 farklı noktası belirli dillere/framework'lere hardcode edilmiş:

**a) `tools/shell_tools.py` → `detect_project_type()`**
```python
def detect_project_type(...) -> str:
    if os.path.exists(os.path.join(workspace_dir, "package.json")):
        return "node"
    if os.path.exists(os.path.join(workspace_dir, "requirements.txt")):
        return "python"
    return "unknown"
```
Sadece 2 dil tanıyor. C++ projesi (`CMakeLists.txt`, `Makefile`), Go projesi (`go.mod`), Rust projesi (`Cargo.toml`), Java projesi (`pom.xml`, `build.gradle`) → hepsi `"unknown"` döner → dependency kurulumu ve build test atlanır.

**b) `tools/shell_tools.py` → `auto_install_dependencies()`**
Sadece `npm install` ve `pip install` çalıştırıyor. C++ için `cmake && make`, Go için `go mod download`, Rust için `cargo build` gibi komutlar yok.

**c) `main.py` → Build test (satır 205)**
```python
if auto_install and detect_project_type() == "node":
    build_result = run_command("npm run build", ...)
```
Sadece Node projelerinde build test çalışıyor. Diğer tüm dillerde build test atlanıyor.

**d) `prompts/tester.md` → React/TypeScript'e özgü**
```
Adım 1: Config Dosyalarını İncele
- vite.config.ts / webpack.config.js → path alias'ları
- tsconfig.json → paths, baseUrl ayarları
- tailwind.config.js → custom renkler
- package.json → mevcut dependency'ler
```
Tester prompt'u doğrudan React/TypeScript/Tailwind dosyalarını referans alıyor. Bir C++ projesinde bunların hiçbiri yok → Tester ne yapacağını bilemez.

**e) `tools/file_tools.py` → `TEXT_EXTENSIONS` ve `IGNORED_DIRS`**
- Eksik uzantılar: `.c`, `.cpp`, `.h`, `.hpp`, `.go`, `.rs`, `.java`, `.kt`, `.swift`, `.rb`, `.php`, `.zig`, `.hs`, `.ex`, `.exs`, `.dart`, `.r`, `.m`, `.mm`
- Eksik ignore dizinleri: `cmake-build-*/`, `target/` (Rust), `bin/`, `obj/`, `vendor/` (Go), `.gradle/`, `out/` (Java)

**f) `tools/file_tools.py` → Config dosyası önceliklendirmesi**
```python
is_config = filename in (
    "package.json", "tsconfig.json", "vite.config.ts",
    "tailwind.config.js", "webpack.config.js", "next.config.js",
    ".eslintrc.json", "pyproject.toml", "requirements.txt",
)
```
Sadece web ve Python config dosyalarını önceliklendiriyor. `CMakeLists.txt`, `Makefile`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle` → önceliksiz.

**Kök neden:** Pipeline ilk olarak bir React portfolio projesi için yazıldı ve o projeye özgü varsayımlar kodun içine sızdı.

### 2.2 KRİTİK: Git Repo Yokluğu

**Durum:** `.gitignore` var ama `git init` yapılmamış.

**Risk:**
- Dosya kaybolursa geri getirilemez
- Değişiklik geçmişi yok
- Committer agent devre dışı çünkü commit atacak repo yok
- GitHub'a pushlanamaz

### 2.3 YÜKSEK: Unit Test Sıfır

**Durum:** Pipeline'ın en kritik fonksiyonları test edilmemiş:
- `save_code_files()` — Coder çıktısını dosyalara yazan parser
- `_parse_json_response()` — Agent yanıtlarını JSON'a çeviren fonksiyon
- `read_workspace_files()` — Context oluşturan fonksiyon
- `read_todolist()` — Task listesi parser'ı
- `detect_project_type()` — Proje tipi algılama
- `save_state()` / `load_state()` — State persistence

**Risk:** Herhangi biri sessizce bozulursa pipeline yanlış çalışır ama hata vermez.

### 2.4 YÜKSEK: State Recovery Yarım Çalışıyor

**Durum:** State'te `step` field'ı kaydediliyor ama hiç kullanılmıyor. Pipeline her zaman planner'dan başlıyor. Tester adımında crash olursa tüm coder-reviewer döngüsü gereksiz yere tekrar çalışıyor.

### 2.5 YÜKSEK: Build Failure Geri Beslenmiyor

**Durum:** Build başarısız olduğunda sadece log'a yazılıp geçiliyor. Coder'a geri gönderilmiyor. Task "TAMAMLANDI" olarak işaretleniyor.

### 2.6 ORTA: Memory.md Sınırsız Büyüyor

**Durum:** Her task sonunda memory'ye append ediliyor. Temizlik mekanizması yok. 100 task sonrası memory devasa → her agent çağrısında token israfı.

### 2.7 ORTA: Token Tracking Toplanmıyor

**Durum:** Agent bazında token sayılıyor ama instance'lar scope'tan çıkınca kayboluyorlar. Pipeline sonunda toplam gösterilmiyor.

---

## 3. Faz 1 — Proje Altyapısı

> **Hedef:** Projeyi versiyon kontrolüne al, dokümante et, test altyapısını kur.
> **Bağımlılık:** Yok — bu faz ilk uygulanmalı.
> **Dokunulacak dosyalar:** `README.md` (yeni), `requirements.txt`, `tests/` (yeni dizin), `tools/__init__.py`

### Adım 1.1 — README.md Oluştur

**Ne:** Projeyi tanımlayan, kurulumu ve kullanımı açıklayan bir README.md yaz.

**Neden:** Projeyi ilk kez gören biri (veya AI agent) ne olduğunu, nasıl çalıştığını bilmeli.

**İçerik yapısı:**
1. Proje başlığı: "Multi-Agent Pipeline — AI-Powered Project Builder"
2. Tek paragraf açıklama: "Workspace'e `memory.md` (proje tanımı) ve `todolist.md` (görev listesi) koyarak herhangi bir dilde proje üretebilen multi-agent AI sistemi."
3. Desteklenen diller/platformlar tablosu (Node, Python, C++, Go, Rust, Java...)
4. Mimari diyagram (ASCII): `Planner → Coder ⇄ Reviewer → Tester → Build → (Committer)`
5. Hızlı başlangıç: git clone, pip install, .env oluştur, workspace hazırla, çalıştır
6. Kullanım örnekleri: `--list`, `--task N`, `--dry-run`, `--verbose`, `--no-install`, `--no-server`
7. Yeni proje başlatma rehberi: workspace temizle, memory.md yaz, todolist.md yaz, çalıştır
8. Konfigürasyon tablosu: config.py'deki her ayar
9. Prompt özelleştirme: prompts/ dosyalarının nasıl düzenleneceği

**Konum:** Proje root'una `README.md`

**Doğrulama:**
- [ ] "Herhangi bir dilde" ifadesi var mı
- [ ] En az 3 farklı dilde örnek senaryo var mı (React, Python, C++)
- [ ] Kurulum adımları (pip install, .env) var mı
- [ ] En az 4 CLI kullanım örneği var mı

### Adım 1.2 — Test Altyapısını Kur

**Ne:** `pytest` ile unit test altyapısı oluştur ve kritik fonksiyonlar için testler yaz.

**Adımlar:**

1. `requirements.txt`'e `pytest>=8.0.0` ekle
2. `tests/` dizini oluştur + `tests/__init__.py` (boş)
3. `tests/test_file_tools.py` oluştur:

   **a) `save_code_files()` testleri (minimum 5):**
   - Normal çıktı → dosyalar doğru kaydediliyor mu?
   - Boş çıktı → hata vermiyor mu?
   - Workspace dışına yazma → engelleniyor mu?
   - Birden fazla dosya → hepsi parse ediliyor mu?
   - Nested code block → doğru parse ediliyor mu?

   **b) `read_workspace_files()` testleri (minimum 4):**
   - Boş dizin → boş string
   - Context limiti → aşılmıyor
   - Config önceliklendirmesi → config dosyaları ilk sırada
   - Ignored dizinler → filtreleniyor

   **c) `read_todolist()` testleri (minimum 3):**
   - Normal format → doğru parse
   - Done/pending → doğru işaretlenme
   - Dosya yok → FileNotFoundError

   **d) `save_state()` / `load_state()` testleri (minimum 3):**
   - Kaydet ve yükle → aynı veri
   - Farklı task → None döner
   - `clear_state()` → dosya siliniyor

4. `tests/test_base_agent.py` oluştur:

   **`_parse_json_response()` testleri (minimum 5):**
   - ` ```json {...} ``` ` → parse
   - ` ```  {...} ``` ` → parse
   - Düz `{...}` → parse
   - Bozuk string → default döner
   - Default'a `raw_response` ekleniyor mu?

5. `tests/test_shell_tools.py` oluştur:

   **`detect_project_type()` testleri (minimum 4):**
   - package.json varsa → "node"
   - requirements.txt varsa → "python"
   - CMakeLists.txt varsa → "cpp" (Faz 2'den sonra)
   - Hiçbiri yoksa → "unknown"

**Doğrulama:**
```bash
python3 -m pytest tests/ -v
```
Tüm testler PASS. Minimum 20 test case.

### Adım 1.3 — tools/__init__.py Export'ları

**Ne:** `tools/__init__.py`'ye export'ları ekle.

**Nasıl:** `agents/__init__.py` ile aynı pattern — `file_tools` ve `shell_tools`'dan ana fonksiyonları export et.

**Doğrulama:**
```python
from tools import read_workspace_files, save_code_files, run_command, detect_project_type
```
Import hata vermemeli.

---

## 4. Faz 2 — Dil-Agnostik Pipeline

> **Hedef:** Pipeline'ı herhangi bir programlama dilinde proje üretebilir hale getir.
> **Bağımlılık:** Faz 1 tamamlanmış olmalı.
> **Dokunulacak dosyalar:** `tools/shell_tools.py`, `tools/file_tools.py`, `main.py`, `prompts/tester.md`, `config.py`
> **KRİTİK:** Bu faz pipeline'ın temel amacını yerine getirmesi için zorunludur.

### Adım 2.1 — Proje Tipi Algılamayı Genişlet

**Ne:** `detect_project_type()` fonksiyonunu tüm yaygın dil/platform'ları tanıyacak şekilde genişlet.

**Neden:** Şu an sadece `"node"` ve `"python"` dönüyor. Kullanıcı C++ projesi yapacaksa → `"unknown"` → dependency kurulumu yok, build test yok, dev server yok.

**Nasıl:**

1. `tools/shell_tools.py`'deki `detect_project_type()` fonksiyonunu yeniden yaz. Algılama tablosu:

   | Dosya | Proje Tipi | Return değeri |
   |---|---|---|
   | `package.json` | Node.js (React, Vue, Next, Express...) | `"node"` |
   | `requirements.txt` veya `pyproject.toml` veya `setup.py` | Python | `"python"` |
   | `CMakeLists.txt` | C++ (CMake) | `"cpp_cmake"` |
   | `Makefile` (ve package.json YOK) | C/C++ (Make) | `"cpp_make"` |
   | `go.mod` | Go | `"go"` |
   | `Cargo.toml` | Rust | `"rust"` |
   | `pom.xml` | Java (Maven) | `"java_maven"` |
   | `build.gradle` veya `build.gradle.kts` | Java/Kotlin (Gradle) | `"java_gradle"` |
   | `*.csproj` veya `*.sln` | C# (.NET) | `"dotnet"` |
   | Hiçbiri | Bilinmeyen | `"unknown"` |

2. Algılama sırası önemli — `package.json` + `Makefile` varsa (Node projesi Make kullanıyor olabilir) → `"node"` döndür. Sıralama: node → python → go → rust → java → cpp → dotnet → unknown

**Doğrulama:**
- Boş dizin oluştur + `CMakeLists.txt` ekle → `"cpp_cmake"` döndürmeli
- `go.mod` ekle → `"go"` döndürmeli
- `package.json` ekle → `"node"` döndürmeli
- Unit test: `test_detect_project_type_all_languages()`

### Adım 2.2 — Dependency Kurulumunu Genişlet

**Ne:** `auto_install_dependencies()` fonksiyonunu tüm proje tipleri için çalışacak şekilde genişlet.

**Neden:** Şu an sadece `npm install` ve `pip install` çalıştırıyor. C++ projesi oluşturulunca dependency kurulumu yok.

**Nasıl:**

1. `auto_install_dependencies()` fonksiyonuna yeni proje tipleri ekle. Kurulum tablosu:

   | Proje Tipi | Kurulum Komutu |
   |---|---|
   | `"node"` | `npm install` |
   | `"python"` | `pip install -r requirements.txt` |
   | `"go"` | `go mod download` |
   | `"rust"` | `cargo fetch` |
   | `"java_maven"` | `mvn dependency:resolve` |
   | `"java_gradle"` | `gradle dependencies` |
   | `"cpp_cmake"` | `mkdir -p build && cd build && cmake ..` |
   | `"cpp_make"` | Kurulum yok (sadece build aşamasında) |
   | `"dotnet"` | `dotnet restore` |
   | `"unknown"` | `None` döndür (kurulum atlanır) |

2. Her komut için uygun timeout değeri ayarla (CMake build uzun sürebilir: 300s)

**Doğrulama:**
- `go.mod` olan bir dizinde → `go mod download` çalıştırılmalı
- Hiçbir config dosyası olmayan dizinde → `None` döndürmeli
- Unit test: `test_auto_install_all_types()`

### Adım 2.3 — Build Test'i Genişlet

**Ne:** `main.py`'deki build testini tüm proje tipleri için çalışacak şekilde genişlet.

**Neden:** Şu an sadece `npm run build` çalışıyor. C++ projesinde build testi yok.

**Nasıl:**

1. `tools/shell_tools.py`'ye yeni fonksiyon ekle:

   ```python
   def get_build_command(project_type: str) -> str | None:
       """Proje tipine göre build komutunu döndür."""
   ```

   Build tablosu:

   | Proje Tipi | Build Komutu |
   |---|---|
   | `"node"` | `npm run build` |
   | `"python"` | `python -m py_compile *.py` (veya `pytest --co` varsa) |
   | `"go"` | `go build ./...` |
   | `"rust"` | `cargo build` |
   | `"java_maven"` | `mvn compile` |
   | `"java_gradle"` | `gradle build` |
   | `"cpp_cmake"` | `cd build && cmake --build .` |
   | `"cpp_make"` | `make` |
   | `"dotnet"` | `dotnet build` |
   | `"unknown"` | `None` (build atlanır) |

2. `main.py`'deki build test bölümünü güncelle:
   - Mevcut: `if detect_project_type() == "node":` → hardcoded
   - Yeni: `build_cmd = get_build_command(detect_project_type())` → dinamik
   - `build_cmd` None ise atla, değilse çalıştır

**Doğrulama:**
- Go projesi → `go build ./...` çalışmalı
- Unknown proje → build atlanmalı
- Unit test: `test_get_build_command()`

### Adım 2.4 — Dev Server Başlatmayı Genişlet

**Ne:** `start_dev_server()` ve ilgili fonksiyonları çoklu dil desteğiyle güncelleyin.

**Neden:** Şu an sadece `npm run dev` ve `python app.py` tanıyor.

**Nasıl:**

1. `_detect_node_start_cmd()` ve `_detect_python_start_cmd()` fonksiyonlarını koruyarak, yeni diller için server algılama ekle:

   | Proje Tipi | Server Komutu | Not |
   |---|---|---|
   | `"node"` | `npm run dev` / `npm start` | Mevcut (çalışıyor) |
   | `"python"` | `python app.py` / `flask run` | Mevcut (çalışıyor) |
   | `"go"` | `go run .` / `go run main.go` | main.go varsa |
   | `"rust"` | `cargo run` | |
   | `"cpp_cmake"` | `./build/main` veya `./build/<proje_adı>` | Build çıktısını bul |
   | `"java_maven"` | `mvn exec:java` | |
   | Diğer | Server yok → atla | |

2. `main.py`'deki port bilgisi çıktısını da dinamikleştir (şu an hardcoded 5173/3000/5000/8000)

**Doğrulama:**
- Go projesi + `main.go` var → `go run .` önerilmeli
- C++ + build başarılı → executable path önerilmeli

### Adım 2.5 — Dosya Uzantılarını ve İgnore Listesini Genişlet

**Ne:** `TEXT_EXTENSIONS`, `IGNORED_DIRS` ve config dosyası önceliklendirmesini tüm dilleri kapsayacak şekilde genişlet.

**Neden:** Şu an C++ `.cpp`/`.h`, Go `.go`, Rust `.rs` dosyaları workspace okumada atlanıyor.

**Nasıl:**

1. `tools/file_tools.py`'deki `TEXT_EXTENSIONS`'a ekle:
   ```python
   # C/C++
   ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
   # Go
   ".go",
   # Rust
   ".rs",
   # Java/Kotlin
   ".java", ".kt", ".kts",
   # C#
   ".cs",
   # Ruby
   ".rb",
   # PHP
   ".php",
   # Swift
   ".swift",
   # Dart
   ".dart",
   # Zig
   ".zig",
   # Makefile/CMake
   ".cmake",
   ```
   NOT: `Makefile` uzantısız olduğu için özel kontrol gerekir → dosya adı `Makefile` veya `CMakeLists.txt` ise oku.

2. `IGNORED_DIRS`'e ekle:
   ```python
   "target",          # Rust
   "vendor",          # Go
   "bin", "obj",      # C#/.NET
   ".gradle", "out",  # Java
   "cmake-build-debug", "cmake-build-release",  # C++ (CLion)
   ```

3. Config dosyası önceliklendirmesine ekle:
   ```python
   is_config = filename in (
       # Mevcut web/python
       "package.json", "tsconfig.json", "vite.config.ts", ...
       # C/C++
       "CMakeLists.txt", "Makefile",
       # Go
       "go.mod", "go.sum",
       # Rust
       "Cargo.toml",
       # Java
       "pom.xml", "build.gradle", "build.gradle.kts",
       # .NET
       # (*.csproj uzantılı — is_config kontrolü uzantıya bakmalı)
   )
   ```
   NOT: `.csproj` uzantılı dosyaları da config olarak işaretle → `or ext in (".csproj", ".sln")` kontrolü ekle.

4. Uzantısız dosyalar için özel kontrol: `Makefile`, `Dockerfile`, `Vagrantfile`, `Gemfile` gibi uzantısız dosyalar da okunmalı.

**Doğrulama:**
- C++ projesi workspace'e koy → `.cpp`, `.h`, `CMakeLists.txt` dosyaları okunuyor mu?
- `CMakeLists.txt` context'te ilk sıralarda mı? (config önceliği)
- `target/` dizini atlanıyor mu?
- Unit test: `test_text_extensions_coverage()`

### Adım 2.6 — Tester Prompt'unu Dil-Agnostik Yap

**Ne:** `prompts/tester.md`'yi herhangi bir dilde çalışacak şekilde yeniden yaz.

**Neden:** Şu an prompt'ta `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `package.json` hardcoded referans alınıyor. Bir C++ projesinde bunların hiçbiri yok → Tester ne yapacağını bilemez.

**Nasıl:**

Tester prompt'undaki "Adım 1: Config Dosyalarını İncele" bölümünü şu şekilde yeniden yaz:

```
Adım 1: Proje Tipini ve Config Dosyalarını Belirle

Workspace dosyalarından projenin DİLİNİ ve TİPİNİ belirle:
- package.json → Node.js/TypeScript projesi → path alias'ları vite/webpack/tsconfig'den kontrol et
- requirements.txt / pyproject.toml → Python projesi → import'ları modül yapısından kontrol et
- CMakeLists.txt / Makefile → C/C++ projesi → include path'leri ve linker flag'larını kontrol et
- go.mod → Go projesi → import path'leri module name'den kontrol et
- Cargo.toml → Rust projesi → use/mod yapısını kontrol et
- pom.xml / build.gradle → Java projesi → package/import yapısını kontrol et

Proje tipini belirledikten sonra, O DİLİN kurallarına göre analiz yap.
Bilmediğin bir dil/framework ise, sadece genel syntax kontrolü yap ve "potential_issue" olarak raporla.
```

"False Positive'den Kaçınma" bölümünü de genelleştir:
```
Bir import'u/include'u "eksik" olarak raporlamadan ÖNCE:
1. Workspace dosyalarında o dosyanın/modülün VARLIĞINI kontrol et
2. Proje config dosyalarından (CMakeLists.txt, go.mod, Cargo.toml, package.json vb.) dependency'leri doğrula
3. Build sistemi config'inden (path alias, include path, module resolution) doğrula
4. Standart kütüphane fonksiyonlarını/modüllerini "eksik" olarak raporlama
```

**Doğrulama:**
- Prompt'ta `vite.config.ts` veya `tailwind.config.js` gibi framework'e özgü referans YOK
- Prompt en az 5 farklı dil/platform'u kapsıyor
- "Bilmediğin dil" durumu için fallback var

---

## 5. Faz 3 — Pipeline Mantık Hataları

> **Hedef:** State recovery, build feedback ve memory yönetimini düzelt.
> **Bağımlılık:** Faz 2 tamamlanmış olmalı.
> **Dokunulacak dosyalar:** `main.py`, `tools/file_tools.py`, `config.py`

### Adım 3.1 — State Recovery'yi Adım-Bazlı Yap

**Ne:** State'teki `step` field'ını kullanarak crash olan task'ı doğru adımdan devam ettir.

**Neden:** Şu an Tester adımında crash olursa, pipeline tekrar Planner ve Coder-Reviewer döngüsünü çalıştırıyor — gereksiz API çağrısı.

**Nasıl:**

1. `save_state()` çağrılarını her adımın SONUNDA yap ve bir SONRAKİ adımı kaydet:
   - Planner tamamlanınca: `save_state(task, "coder", {"plan": plan})`
   - Coder-Reviewer tamamlanınca: `save_state(task, "tester", {"plan": plan, "code": code})`
   - Tester tamamlanınca: `save_state(task, "build", {"plan": plan, "code": code})`

2. `run_single_task()` başında step'e göre dallan:
   - `step == "coder"` → plan state'ten, coder-reviewer döngüsüne git
   - `step == "tester"` → plan+code state'ten, tester'a git
   - `step == "build"` → plan+code state'ten, build'e git
   - `step == "done"` veya state yok → baştan başla

3. Her dallanmada atlanan adımları print et: `"  Planner atlandı (state'ten yüklendi)"`

**Doğrulama:**
1. State dosyasını `{"task": "test", "step": "tester", "plan": "...", "code": "..."}` olarak oluştur
2. Pipeline'ı çalıştır → Planner ve Coder atlanmalı, direkt Tester'dan başlamalı
3. Unit test: Her step değeri için doğru dallanma

### Adım 3.2 — Build Failure Feedback Loop

**Ne:** Build başarısız olduğunda, hata çıktısını Coder'a gönder ve düzeltme döngüsüne sok.

**Neden:** Şu an build hatası sadece log'a yazılıyor. Coder'ın düzeltme şansı yok.

**Nasıl:**

1. Build testi Coder-Reviewer döngüsünden SONRA, Tester'dan ÖNCE çalışmalı (çünkü build gerçek compiler hatalarını yakalar)

2. Build başarısız olduğunda:
   - Build hata çıktısını (stderr) reviewer feedback formatına çevir
   - Coder'ın `fix()` metoduna gönder
   - Düzeltilmiş kodu tekrar build et
   - `config.py`'ye `MAX_BUILD_RETRIES = 2` ekle
   - 2 retry sonra hâlâ fail → log'a yaz ve devam et

3. Feedback formatı:
   ```python
   build_feedback = {
       "approved": False,
       "score": 2,
       "summary": f"Build hatası: {project_type}",
       "issues": [{
           "severity": "critical",
           "file": "build output",
           "description": stderr[:2000],
           "fix": "Build hatasını düzelt"
       }]
   }
   ```

**Doğrulama:**
1. Workspace'e bilerek bozuk kod yaz
2. Pipeline çalıştır → Build fail → Coder'a feedback → Coder düzeltir → Build tekrar
3. Düzeltme sonrası build PASS olmalı

### Adım 3.3 — Memory.md Boyut Kontrolü

**Ne:** Memory.md'nin sınırsız büyümesini engelleyen truncation mekanizması ekle.

**Nasıl:**

1. `config.py`'ye: `MAX_MEMORY_LINES = 100`
2. `update_memory()` fonksiyonunda:
   - Memory'yi oku, satır say
   - Limit aşılıyorsa → en eski `## Task Tamamlandı:` bloklarını sil (FIFO)
   - Proje tanımı bölümünü (ilk `## Task` öncesi) KORU
   - Kırpılan yere `(Eski kayıtlar kırpıldı — detaylar logs/ altında)` notu ekle

**Doğrulama:**
1. 120 satırlık memory oluştur → `update_memory()` çağır → 100 satırın altında mı?
2. Proje tanımı korunmuş mu?
3. Unit test: `test_memory_truncation()`

---

## 6. Faz 4 — Agent Kalitesi ve Prompt Mühendisliği

> **Hedef:** Agent'ların çıktı kalitesini artır, Committer'ı dönüştür.
> **Bağımlılık:** Faz 3 tamamlanmış olmalı.
> **Dokunulacak dosyalar:** `prompts/committer.md`, `prompts/reviewer.md`, `prompts/planner.md`, `agents/committer.py`, `config.py`, `main.py`

### Adım 4.1 — Committer → Memory Updater'a Dönüştür

**Ne:** Committer agent'ı devre dışı bırakmak yerine, Memory.md'yi akıllıca güncelleyen bir agent'a dönüştür.

**Neden:** `update_memory()` sadece mekanik bilgi yazıyor ("Task X tamamlandı, dosyalar: Y"). Bir AI agent'ın memory'yi özetlemesi, önemli kararları ve pattern'ları kaydetmesi sonraki task'lar için çok daha değerli.

**Nasıl:**

1. `prompts/committer.md` yeniden yaz:
   - Görev: Task'ta ne yapıldığını özetle, sonraki task'lar için önemli bilgileri not et
   - Çıktı formatı: `{"memory_entry": "...", "important_patterns": [...]}`
   - Kurallar: Mevcut memory ile çakışma yapma, gereksiz bilgi ekleme, kısa tut

2. `agents/committer.py`'de `commit()` yerine `summarize()` metodu yaz:
   - Input: task, code, review özeti
   - Output: memory girişi

3. `main.py`'de Committer çağrısını güncelle:
   - Committer çıktısındaki `memory_entry`'yi memory.md'ye yaz
   - Mevcut `update_memory()` çağrısını kaldır (Committer yapacak)

4. `config.py`'de `ENABLE_COMMITTER = True` yap, model `claude-haiku` kalsın

**Doğrulama:**
1. Task çalıştır → Memory'deki yeni giriş anlamlı ve kısa mı?
2. Haiku maliyeti kabul edilebilir mi? (~500 token output)

### Adım 4.2 — Planner'dan İlgili Dosya Listesi

**Ne:** Planner çıktısından hangi dosyaların bu task ile ilgili olduğunu çıkar, sadece onları Coder'a gönder.

**Neden:** Tüm workspace (~80K char) her agent'a gönderiliyor. Bir task genelde 3-5 dosyayla ilgili.

**Nasıl:**

1. `prompts/planner.md`'ye ekle:
   ```
   ## İlgili Dosyalar
   Coder'ın görmesi GEREKEN mevcut dosyaları listele:
   - RELEVANT: path/to/file — neden gerekli
   Coder'ın görmesine GEREK OLMAYAN dosyaları listeleme.
   ```

2. `main.py`'de plan çıktısından `RELEVANT:` satırlarını ayıkla

3. İlgili dosya listesi boşsa → fallback: tüm workspace (mevcut davranış)

4. Liste doluysa → `read_specific_files(relevant_list)` ile sadece o dosyaları Coder'a gönder (bu fonksiyonu `file_tools.py`'ye ekle)

**Doğrulama:**
1. Planner çıktısında `RELEVANT:` satırları var mı?
2. Coder'a gönderilen token sayısı azaldı mı?

### Adım 4.3 — Reviewer'a Zorunlu Regresyon Raporu

**Ne:** Reviewer JSON çıktısına zorunlu `regression_check` field'ı ekle.

**Nasıl:**

1. `prompts/reviewer.md`'deki JSON formatına ekle:
   ```json
   "regression_check": {
     "checked": true,
     "files_compared": ["dosya1", "dosya2"],
     "regressions_found": []
   }
   ```

2. `main.py`'de review sonucunda `regression_check` kontrol et:
   - Field yoksa → uyarı yazdır
   - `regressions_found` doluysa → her birini issue olarak logla

**Doğrulama:** Reviewer çıktısında `regression_check` field'ı mevcut mu?

---

## 7. Faz 5 — Token Ekonomisi ve Maliyet Optimizasyonu

> **Hedef:** Token kullanımını izle ve raporla.
> **Bağımlılık:** Faz 4 tamamlanmış olmalı.
> **Dokunulacak dosyalar:** `main.py`, `config.py`

### Adım 5.1 — Pipeline-Seviye Token Tracking

**Ne:** Pipeline sonunda toplam token kullanımını ve tahmini maliyeti göster.

**Neden:** Agent instance'ları scope'tan çıkınca token bilgisi kayboluyor.

**Nasıl:**

1. `main.py`'de pipeline seviyesinde sayaç:
   ```python
   pipeline_tokens = {"input": 0, "output": 0, "api_calls": 0}
   ```

2. `run_single_task()` return değerine token bilgisi ekle:
   - Her agent çalıştıktan sonra, agent'ın `total_input_tokens` ve `total_output_tokens` değerlerini topla
   - Task bitince bu toplamı döndür

3. Pipeline raporuna ekle:
   ```
   PIPELINE RAPORU
   ═══════════════
   Toplam: 3 başarılı, 0 başarısız
   API Çağrıları: 15
   Token: 45,200 input + 12,800 output = 58,000 toplam
   Tahmini Maliyet: ~$0.87
   ```

4. Maliyet tahmini (yaklaşık birim fiyatlar):
   - Sonnet: input $3/1M, output $15/1M
   - Haiku: input $0.25/1M, output $1.25/1M

**Doğrulama:** Pipeline çalıştır → Raporda token ve maliyet bilgisi var mı?

### Adım 5.2 — JSON Pipeline Raporu

**Ne:** Pipeline sonucunu `logs/pipeline_report_YYYY-MM-DD_HH-MM.json` olarak kaydet.

**Nasıl:**
```python
report = {
    "timestamp": "...",
    "tasks": [{"name": "...", "success": True, "tokens": {...}}],
    "totals": {"success": N, "failed": M, "tokens": {...}, "cost_usd": X}
}
```

**Doğrulama:** `python3 -m json.tool logs/pipeline_report_*.json` → Valid JSON mi?

---

## 8. Faz 6 — Yeni Yetenekler

> **Hedef:** Kullanıcı deneyimini artıran yeni özellikler.
> **Bağımlılık:** Faz 5 tamamlanmış olmalı.
> **Dokunulacak dosyalar:** `main.py`, `config.py`, `agents/base.py`

### Adım 6.1 — --verbose Flag

**Ne:** `--verbose` flag'i ile debug çıktısı göster.

**Nasıl:**

1. `main.py` argparse'a `--verbose` ekle
2. `config.py`'ye `VERBOSE = False` ekle (runtime'da args'tan override)
3. `agents/base.py` → verbose modda:
   - Gönderilen mesajın ilk 500 char'ını yazdır
   - Alınan yanıtın ilk 500 char'ını yazdır
   - System prompt boyutunu yazdır

**Doğrulama:** `--verbose --dry-run` ile çalıştır → ek çıktı var, `--dry-run` ile çalıştır → ek çıktı yok.

### Adım 6.2 — Workspace Sıfırlama Komutu

**Ne:** `--reset` flag'i ile workspace'i temizleyip yeni projeye hazırla.

**Neden:** Kullanıcı React projesinden C++ projesine geçerken workspace'i manuel temizlemesi gerekiyor. Otomatik sıfırlama komutu olmalı.

**Nasıl:**

1. `main.py`'ye `--reset` argümanı ekle
2. `--reset` çalıştığında:
   - Kullanıcıya onay sor: "Workspace silinecek. Emin misiniz? (y/n)"
   - workspace/ altındaki TÜM dosyaları sil (memory.md ve todolist.md HARİÇ)
   - Eğer `--reset --full` ise: memory.md ve todolist.md dahil sil, boş şablon oluştur
   - State dosyasını temizle (`clear_state()`)
   - Logs temizlenmez (geçmiş korunur)

3. Boş şablon oluştur:
   ```markdown
   # memory.md
   ## Proje Tanımı
   [Proje açıklamanı buraya yaz]

   ## Teknoloji Seçimleri
   [Kullanılacak dil, framework, araçlar]
   ```

**Doğrulama:**
- `--reset` → workspace dosyaları silindi, memory.md ve todolist.md korundu
- `--reset --full` → her şey silindi, boş şablonlar oluşturuldu
- logs/ dizini korundu

### Adım 6.3 — Workspace Validation

**Ne:** Pipeline başlamadan önce workspace'in geçerliliğini kontrol et.

**Nasıl:**

1. `main.py`'ye `validate_workspace()` fonksiyonu:
   - workspace/ dizini var mı?
   - todolist.md var ve parse edilebiliyor mu?
   - memory.md var mı? (yoksa boş oluştur + uyarı)
   - En az 1 pending task var mı?

2. Pipeline başında çağır → kritik hata varsa açıklayıcı mesajla çık

**Doğrulama:**
- workspace/ yok → "workspace bulunamadı" hatası
- todolist.md yok → açıklayıcı hata mesajı
- memory.md yok → uyarı + boş dosya oluşturuldu

---

## 9. Final Checklist ve Kabul Kriterleri

Tüm fazlar tamamlandıktan sonra aşağıdaki kontrol listesini çalıştır. **HEPSİ geçmeli:**

### Altyapı
- [ ] `README.md` mevcut ve "herhangi bir dilde proje üretebilir" ifadesi var
- [ ] `python3 -m pytest tests/ -v` → Tüm testler PASS (minimum 20 test)
- [ ] `tools/__init__.py` export'ları çalışıyor

### Dil-Agnostik Pipeline
- [ ] `detect_project_type()` en az 8 proje tipini tanıyor (node, python, cpp_cmake, cpp_make, go, rust, java_maven, java_gradle)
- [ ] `auto_install_dependencies()` her tanınan proje tipi için doğru komutu çalıştırıyor
- [ ] `get_build_command()` her tanınan proje tipi için doğru komutu döndürüyor
- [ ] `TEXT_EXTENSIONS` C++ (.cpp, .h), Go (.go), Rust (.rs), Java (.java) dosyalarını içeriyor
- [ ] `IGNORED_DIRS` target/ (Rust), vendor/ (Go), cmake-build-*/ (C++) dizinlerini içeriyor
- [ ] Config önceliklendirmesi CMakeLists.txt, go.mod, Cargo.toml, pom.xml dosyalarını tanıyor
- [ ] `prompts/tester.md` hiçbir dile/framework'e hardcoded referans içermiyor
- [ ] `prompts/tester.md` en az 5 farklı dil için config dosyası algılama talimatı içeriyor

### Pipeline Doğruluğu
- [ ] State recovery adım-bazlı çalışıyor (step=tester → planner+coder atlanıyor)
- [ ] Build failure → Coder'a feedback gönderiliyor → düzeltme döngüsü
- [ ] Memory.md MAX_MEMORY_LINES'ı aşmıyor (auto-truncation)

### Agent Kalitesi
- [ ] Committer → Memory updater olarak çalışıyor
- [ ] Planner çıktısında `RELEVANT:` dosya listesi var
- [ ] Reviewer çıktısında `regression_check` field'ı var

### Token Ekonomisi
- [ ] Pipeline raporu token toplamı gösteriyor
- [ ] Pipeline raporu tahmini maliyet gösteriyor
- [ ] JSON rapor dosyası `logs/` altında oluşuyor

### UX
- [ ] `--verbose` çalışıyor
- [ ] `--reset` workspace'i temizliyor
- [ ] `--reset --full` şablonlar oluşturuyor
- [ ] Workspace validation çalışıyor

### Dil Testleri (Manuel)
- [ ] Boş workspace + Python memory/todolist → Python projesi üretiliyor
- [ ] Boş workspace + C++ memory/todolist → C++ projesi üretiliyor (en azından dosyalar oluşuyor)
- [ ] Boş workspace + Go memory/todolist → Go projesi üretiliyor

---

## Tahmini Etki Matrisi

```
                          ÖNCESİ            SONRASI
                          ═══════            ═══════
Desteklenen diller:       2 (Node, Python) → 8+ (Node, Python, C++, Go, Rust, Java, C#, Make)
Build test kapsamı:       Sadece Node      → Tüm tanınan diller
Tester dil bağımlılığı:   React/TS'ye bağlı → Dil-agnostik
Dosya uzantı kapsamı:     Web + Python     → 20+ dil
State recovery:           Yarım            → Adım-bazlı tam recovery
Build hata yakalama:      Bilgi amaçlı     → Feedback loop (Coder düzeltir)
Token görünürlüğü:        Yok              → Pipeline raporu + maliyet
Memory kontrolü:          Sınırsız         → Auto-truncate (100 satır)
Debug kolaylığı:          Zor              → --verbose
Workspace yönetimi:       Manuel           → --reset / --reset --full
Unit test:                %0               → %60+ (kritik fonksiyonlar)
```

---

*Bu doküman, pipeline'ın genel amaçlı bir proje oluşturucu olduğu felsefesiyle yazılmıştır. Her adım dil-agnostik olacak şekilde tasarlanmıştır. Workspace'e koyduğun memory.md ve todolist.md ne derse, pipeline onu üretebilmelidir.*
