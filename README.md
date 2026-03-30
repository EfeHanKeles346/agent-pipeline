# Multi-Agent Pipeline — AI-Powered Project Builder

`memory.md` ile proje bağlamını, `todolist.md` ile görev listesini vererek herhangi bir dilde proje üretebilmeyi hedefleyen multi-agent bir AI pipeline. Mevcut implementation artık Node.js, Python, C++, Go, Rust, Java ve .NET proje tiplerini algılayıp uygun install/build akışları seçebiliyor; yol haritasının kalan mantık iyileştirmeleri [`improvements.md`](./improvements.md) içinde izleniyor.

## Ne Yapar?

- `workspace/memory.md` içindeki proje tanımını okur
- `workspace/todolist.md` içindeki pending task'ları sırayla işler
- Planner, Coder, Reviewer ve Tester agent'larıyla kod üretir
- Çıktıları `workspace/` içine yazar
- Log ve state dosyalarıyla süreci izlenebilir hale getirir

## Desteklenen Diller ve Platformlar

| Dil / Platform | Bugünkü Durum | Not |
|---|---|---|
| Node.js / React / TypeScript | Hazır | `package.json`, install, build ve dev command algısı aktif |
| Python | Hazır | `requirements.txt`, `pyproject.toml`, `setup.py` algısı aktif |
| C++ | Destekleniyor | `CMakeLists.txt` ve `Makefile` tabanlı algılama aktif |
| Go | Destekleniyor | `go.mod` algısı ve build/install komutları aktif |
| Rust | Destekleniyor | `Cargo.toml` algısı ve build/install komutları aktif |
| Java / Kotlin | Destekleniyor | Maven ve Gradle marker'ları algılanıyor |
| .NET | Destekleniyor | `*.csproj` / `*.sln` algısı ve build/install komutları aktif |

Bu proje tasarım gereği herhangi bir dilde proje üretebilir hale gelmek üzere yapılandırılıyor. Örnek senaryolar:

- React portfolio sitesi
- Python CLI tool
- C++ ray tracer

## Mimari

```text
memory.md + todolist.md
          |
          v
   Planner Agent
          |
          v
   Coder Agent <----> Reviewer Agent
          |
          v
     Tester Agent
          |
          v
      Build Check
          |
          v
   workspace/ output
```

## Hızlı Başlangıç

```bash
git clone https://github.com/EfeHanKeles346/agent-pipeline.git
cd agent-pipeline
python3 -m pip install -r requirements.txt
cp .env.example .env
```

`.env` içine API key ekleyin:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Sonra `workspace/memory.md` ve `workspace/todolist.md` dosyalarını hazırlayıp pipeline'ı çalıştırın:

```bash
python3 main.py
```

## CLI Kullanımı

Bugün kullanılabilen komutlar:

```bash
python3 main.py --list
python3 main.py --task 1
python3 main.py --dry-run
python3 main.py --no-install
python3 main.py --no-server
```

Yol haritasındaki ek komutlar:

```bash
python3 main.py --verbose   # Faz 6
python3 main.py --reset     # Faz 6
```

## Yeni Proje Başlatma Rehberi

1. `workspace/` içindeki mevcut hedef projeyi temizleyin veya değiştirin.
2. `workspace/memory.md` içine proje tanımını yazın.
3. `workspace/todolist.md` içine yapılacak işleri `- [ ] ...` formatında ekleyin.
4. `python3 main.py --list` ile görevleri kontrol edin.
5. `python3 main.py` ile pipeline'ı çalıştırın.

Örnek `memory.md` fikirleri:

- "React + TypeScript ile responsive portfolio sitesi"
- "Python ile tek dosyalık log analiz CLI aracı"
- "C++ ile basic ray tracer"

## Workspace Dosyaları

- `workspace/memory.md`: Projenin amacı, mimarisi, kısıtları
- `workspace/todolist.md`: Uygulanacak görevler
- `workspace/`: Üretilen hedef proje

## Konfigürasyon

Tüm ana ayarlar [`config.py`](./config.py) içindedir.

| Ayar | Açıklama |
|---|---|
| `API_KEY` | `ANTHROPIC_API_KEY` environment variable üzerinden okunur |
| `MODELS` | Her agent için model seçimi |
| `MAX_REVIEW_ATTEMPTS` | Reviewer reddederse coder düzeltme turu sayısı |
| `ENABLE_TESTER` | Tester agent aç/kapat |
| `ENABLE_COMMITTER` | Committer agent aç/kapat |
| `TASK_COOLDOWN_SECONDS` | Task'lar arası bekleme süresi |
| `PIPELINE_DIR` | Projenin root dizini |
| `PROMPTS_DIR` | Agent prompt klasörü |
| `WORKSPACE_DIR` | Hedef proje klasörü |
| `TODOLIST_FILE` | Görev listesi dosyası |
| `MEMORY_FILE` | Proje bağlam dosyası |
| `LOGS_DIR` | Task log klasörü |
| `AUTO_INSTALL` | Otomatik bağımlılık kurulumu |
| `AUTO_DEV_SERVER` | Tüm task'lar bitince dev server başlatma |
| `SEND_WORKSPACE_CONTEXT` | Workspace dosyalarını agent context'ine ekleme |
| `MAX_TOKENS` | Agent başına max output token |
| `MAX_WORKSPACE_CONTEXT_CHARS` | Workspace context toplam karakter limiti |
| `MAX_FILE_SIZE` | Tek dosya için maksimum context boyutu |

## Prompt Özelleştirme

Agent davranışı `prompts/` altındaki markdown dosyalarıyla şekillenir:

- `prompts/planner.md`
- `prompts/coder.md`
- `prompts/reviewer.md`
- `prompts/tester.md`
- `prompts/committer.md`

Bu dosyaları değiştirerek:

- Kodlama stilini
- Reviewer sertliğini
- Tester analiz şeklini
- Planner çıktı formatını

özelleştirebilirsiniz.

## Testler

Unit testleri çalıştırmak için:

```bash
python3 -m pytest tests/ -v
```

Test kapsamı şu an kritik parser ve tool fonksiyonlarına odaklanır:

- `save_code_files()`
- `read_workspace_files()`
- `read_todolist()`
- `save_state()` / `load_state()` / `clear_state()`
- `BaseAgent._parse_json_response()`
- `detect_project_type()`

## Notlar

- `logs/` klasörü task geçmişini tutar
- `.pipeline_state.json` yarım kalan task'ı toparlamak için kullanılır
- `workspace/node_modules` ve `workspace/dist` git'e dahil edilmez
- Yol haritası ve kabul kriterleri için [`improvements.md`](./improvements.md) dosyasına bakın
