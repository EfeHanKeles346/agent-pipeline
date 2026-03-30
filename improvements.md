# Multi-Agent Pipeline — Yeni Improvements Raporu

**Tarih:** 2026-03-31
**Durum:** Faz 1-6 tamamlandi, repo public, bundled demo workspace kaldirildi
**Amac:** Bundan sonra projeyi nasil daha kullanisli, daha ucuz test edilebilir ve gercek is teslimine daha yakin hale getirecegimizi netlestirmek

---

## 1. Bu Rapor Neden Yazildi?

Ilk `improvements.md`, projeyi kirilgan ve dil-bagimli bir durumdan bugunku daha saglam hale getirmek icin yazilmisti. O rapordaki ana fazlar uygulandi:

- git repo kuruldu
- README ve test altyapisi eklendi
- pipeline coklu dil destekler hale geldi
- build feedback loop ve step-based recovery eklendi
- planner/reviewer/committer tarafi guclendirildi
- token ve maliyet raporlamasi eklendi
- `--verbose`, `--reset`, validation gibi UX ozellikleri eklendi

Bu yeni raporun gorevi artik "temel eksikleri kapat" degil, su soruya cevap vermektir:

**Bu projeyi nasil gercek islerde kullanilabilir, ucuz test edilebilir ve ileride urunlestirilebilir hale getiririz?**

---

## 2. Entegrasyon Oncesi Ne Anladik?

Yeni bir entegrasyona veya buyuk feature'a baslamadan once su noktalar net:

### 2.1 Bu repo artik "demo site generator" degil

Bu proje bir web template repo'su degil. Artik cekirdekte su fikir var:

- Kullanici `workspace/memory.md` ile proje amacini verir
- `workspace/todolist.md` ile isi gorev parcalarina ayirir
- pipeline bunu agent orchestration ile uygular
- build, review, memory ve log sistemi sonucu izler

Yani asil urun: **AI orchestrator engine**

### 2.2 Workspace ciktisi ile pipeline cekirdegi ayri tutulmali

Bu cok kritik. `workspace/` icindeki proje:

- degisken
- disposable
- repoya bagli olmamali
- portfolyo dili istatistigini bozmamali

Bu nedenle demo website'nin kaldirilmasi dogru bir karar oldu.

### 2.3 En buyuk risk artik "feature eksigi" degil

Simdi asagidaki riskler daha kritik:

- API maliyeti nedeniyle gelistirme hizinin dusmesi
- gercek agent kalitesinin deterministik test edilememesi
- her yeni feature'da canli model cagrisi gereksinimi
- "calisan kod" ile "teslim edilebilir MVP" arasindaki fark

### 2.4 C++ destegi kozmetik degil

C++'in eklenmesi bir "fazlalik" degil; projeyi gercekten dil-agnostik yapma hedefinin parcasi. Bu repo sadece web app degil:

- Python tool
- Go service
- Rust utility
- C++ CLI / engine / library

gibi ciktilari da hedefleyebilmeli.

### 2.5 Bu proje iki ayri hedefe ayni anda yuruyor

Bugun iki kullanim hedefi gorunuyor:

1. **Kisisel teslim motoru**
   Burada amac, kendi projelerinde ve musteri islerinde hiz kazanmak.

2. **Portfolyoluk urun**
   Burada amac, "AI ile is teslim pipeline'i" olarak guven veren bir urun gostermek.

Bu iki hedef birbiriyle uyumlu, ama roadmap siralamasi dogru olmali:

- once ic kullanim
- sonra guvenilirlik
- sonra urunlestirme

---

## 3. Proje Su An Hangi Yeteneklere Sahip?

Bugunku net capability haritasi:

### 3.1 Orchestration

- Planner -> Coder <-> Reviewer -> Build -> Tester -> Memory flow
- state persistence
- step-based recovery
- task bazli ilerleme

### 3.2 Coklu Dil / Platform

- Node.js
- Python
- Go
- Rust
- Java Maven
- Java Gradle
- C++ CMake
- C++ Make
- .NET

### 3.3 Kod ve Context Yonetimi

- workspace dosyalarini okuyabilme
- planner `RELEVANT:` listesine gore targeted context
- generated code'lari kaydetme
- memory truncation

### 3.4 Guvenilirlik

- review retry loop
- build failure -> coder feedback loop
- regression normalization
- unit test coverage

### 3.5 Gozlemlenebilirlik

- task log'lari
- JSON pipeline report
- token / api_calls / maliyet ozeti
- verbose debug ciktilari

### 3.6 UX

- `--list`
- `--task`
- `--dry-run`
- `--no-install`
- `--no-server`
- `--verbose`
- `--reset`
- `--reset --full`
- workspace validation

Kisa sonuc:

**Cekirdek motor olusmus durumda.**

Eksik olan kisim:

**ucuz test, gercek teslim kalitesi ve urunlestirme katmani**

---

## 4. En Buyuk Aciklar

Buradan sonraki en buyuk aciklar su basliklarda:

### 4.1 Ucretsiz veya cok dusuk maliyetli gelistirme modu yok

Bugun pipeline'i gelistirirken asil maliyet yaratan kisim model cagrilari. Bu da su sonuca yol acar:

- prompt denemesi pahali
- loop denemesi pahali
- bugfix denemesi pahali
- ogrenci butcesi icin iterasyon zor

### 4.2 Gercek "MVP delivery" modu yok

Pipeline kod uretebilir, ama bugunku haliyle henuz su paketi garanti etmiyor:

- auth
- db
- migrations
- seed data
- deploy instructions
- handoff docs
- smoke-tested route listesi

### 4.3 Provider bagimliligi var

Core agent execution su an tek provider ekseninde dusunulmus durumda. Bu, asagidaki imkanlari kisitliyor:

- local model ile test
- ucuz model ile preview
- mock provider ile fixture run

### 4.4 E2E senaryo kutuphanesi yok

Gercek kaliteyi olcmek icin su tipte fixture setleri olmali:

- Python CLI
- Go API
- C++ CLI
- full-stack dashboard
- landing page + admin panel

Bugun bunlar belge seviyesinde dusunulebiliyor, ama pipeline icinde standart benchmark olarak yok.

### 4.5 Handoff kalitesi standardize degil

Bir musteri isinde aslinda sadece kod yetmez. Teslim paketi de lazim:

- README
- setup guide
- `.env.example`
- demo data
- build/run instructions
- known limitations

---

## 5. Ucretsiz Test Mantigi: Neden Gerekli?

Bu proje icin "ucretsiz test" fikri bir yan konu degil, stratejik konu.

Asil mantik su:

### 5.1 Iki farkli seyi ayirmamiz lazim

1. **Engine dogrulugu**
   Pipeline akisi, state, parser, log, build, memory, reset, validation gibi mekanikler

2. **Model kalitesi**
   Planner'in ne kadar iyi planladigi, coder'in ne kadar iyi kod yazdigi, reviewer'in ne kadar iyi issue buldugu

Bugun engine ve model birbirine fazla bagli. Oysa engine tarafinin buyuk kismi aslinda API'siz test edilebilir.

### 5.2 Ucretsiz testin hedefi "modeli bedava degistirmek" degil

Hedef su:

- canli API kullanmadan pipeline gelistirebilmek
- prompt cikti formatlarini fixture ile test edebilmek
- build/review/memory loop'larini ucuzca denemek
- yalnizca final kalite kontrolunde gercek modele gitmek

### 5.3 Dogru strateji: canli cagrilari en sona birakmak

Buna gore gelistirme akisi su olmali:

1. mock / fixture ile engine testi
2. local validator ile output sekli testi
3. replay mode ile onceki run'larin tekrar test edilmesi
4. en sonda kisa canli model denemesi

Bu sayede maliyet ciddi sekilde duser.

---

## 6. Ucretsiz Test Icin Neler Yapilabilir?

Burasi bundan sonraki en onemli teknik alan.

### 6.1 Mock Mode

Yeni bir mod:

```text
python3 main.py --mock
```

Bu modda agent'lar gercek API'ye gitmez. Yerine:

- `fixtures/planner/*.md`
- `fixtures/coder/*.md`
- `fixtures/reviewer/*.json`
- `fixtures/tester/*.json`
- `fixtures/committer/*.json`

gibi sabit dosyalardan cevap okur.

**Ne kazandirir?**

- sifir API maliyeti
- deterministik test
- bug tekrar uretilebilirligi

### 6.2 Scenario Pack Sistemi

`fixtures/scenarios/` altinda senaryo klasorleri:

- `python_cli/`
- `cpp_tool/`
- `go_service/`
- `web_dashboard/`

Her senaryoda:

- `memory.md`
- `todolist.md`
- beklenen planner cevabi
- beklenen coder cevabi
- review/test cevaplari

olur.

Bu sayede pipeline'i ayni brief'lerle tekrar tekrar deneyebilirsin.

### 6.3 Replay Mode

Gercek bir canli run sirasinda agent cevaplarini kaydet:

- `logs/replays/...`

Sonra su modla tekrar oyna:

```text
python3 main.py --replay logs/replays/run_001
```

Bu sayede bir kez para harcanan run, sonraki engine gelistirmelerinde bedavaya tekrar kullanilir.

### 6.4 Local Provider Desteği

Ikinci asama olarak:

- Ollama
- LM Studio
- llama.cpp benzeri lokal modeller

icin provider layer eklenebilir.

Bu modeller her zaman en iyi kaliteyi vermez, ama:

- prompt sekli denemesi
- pipeline akisi denemesi
- dusuk riskli prototip

icin cok faydali olabilir.

### 6.5 Schema Validation

Her agent icin beklenen output yapisi zorlanmali:

- planner -> markdown + `RELEVANT:` satirlari
- reviewer -> zorunlu JSON alanlari
- tester -> zorunlu JSON alanlari
- committer -> `memory_entry`, `important_patterns`

Bu validation API'siz olarak da test edilebilir.

### 6.6 Golden Testler

Belirli prompt input'larina karsi:

- cikti format bozuldu mu?
- zorunlu alanlar kayboldu mu?
- parse edilebilirlik bozuldu mu?

gibi kontroller yapilabilir.

Bu, prompt refactor ederken cok degerli olur.

---

## 7. Projeye Entegre Etmeden Once Onerilen Tasarim

Ucretsiz test sistemini dogrudan yamali sekilde degil, temiz bir mimariyle eklemek lazim.

### 7.1 Provider Katmani

Bugun agent mantigi ile provider mantigi ic ice. Bunu ayirmak iyi olur:

```text
agents/
providers/
  anthropic_provider.py
  mock_provider.py
  replay_provider.py
  ollama_provider.py
```

`BaseAgent`, direkt API client yerine provider interface'i kullanir.

### 7.2 Run Mode Kavrami

Config veya CLI seviyesinde bir run mode olmali:

- `live`
- `mock`
- `replay`
- `local`

Bu, ileride karmasayi azaltir.

### 7.3 Fixture Formatini Simdiden Standardize Etmek

Sonradan kirilmamasi icin fixture formatini erken belirlemek lazim:

- planner -> `.md`
- coder -> `.md`
- reviewer/tester/committer -> `.json`
- metadata -> `scenario.json`

### 7.4 Senaryo Basina Beklenen Sonuc Yazmak

Her senaryo icin asagidaki gibi bir metadata mantikli:

```json
{
  "name": "python_cli",
  "project_type": "python",
  "should_build": true,
  "should_test_pass": true,
  "expected_files": ["main.py", "README.md"]
}
```

Bu sayede agent cevabinin kalitesini de kismen olcebilirsin.

---

## 8. Yeni Roadmap Onerisi

Asagidaki siralamayi oneriyorum.

### Faz A — Ucretsiz Validation Katmani

**Oncelik:** En yuksek

Hedefler:

- `--mock`
- fixture response sistemi
- replay mode
- schema validation
- golden tests

Bu fazin amaci:

**para harcamadan gelistirme hizi kazanmak**

### Faz B — Provider Soyutlama

Hedefler:

- anthropic provider'i ayir
- mock provider ekle
- replay provider ekle
- local provider icin hazir altyapi kur

Bu fazin amaci:

**tek provider bagimliligini azaltmak**

### Faz C — Gercek Senaryo Kutuphanesi

Hedefler:

- Python CLI fixture
- Go service fixture
- C++ tool fixture
- web MVP fixture

Bu fazin amaci:

**kaliteyi olculebilir hale getirmek**

### Faz D — MVP Delivery Mode

Hedefler:

- web app blueprint
- auth + db + dashboard template
- standard handoff files
- `.env.example`, README, setup guide uretimi

Bu fazin amaci:

**musteriye verilebilir MVP ciktilari almak**

### Faz E — Systems Mode

Hedefler:

- C++ CLI/library senaryolari
- CMake presets
- test/benchmark scaffolding
- daha guclu compile validation

Bu fazin amaci:

**web disi projelerde de guven kazanmak**

### Faz F — Safety ve Operasyon

Hedefler:

- temp workspace
- snapshot / rollback
- command allowlist
- diff preview

Bu fazin amaci:

**canli islerde guvenli kullanmak**

---

## 9. Maliyet Dusurme Stratejisi

Tamamen "bedava kaliteli model" bulmak zor olabilir. O yuzden daha gercekci strateji:

### 9.1 Sifir Maliyetli Katman

- dry-run
- mock mode
- replay mode
- unit tests
- schema tests
- build/test automation

### 9.2 Cok Dusuk Maliyetli Katman

- local model ile kaba deneme
- kucuk provider ile sekil kontrolu
- sadece planner/reviewer'i canli cagirip coder'i fixture ile test etmek gibi hibrit modlar

### 9.3 Ucretli Ama Kontrollu Katman

- sadece final canli generation
- sadece secili senaryolarda live validation
- sadece release oncesi smoke run

Bu uc katman kurulursa, her degisiklikte para yakmak zorunda kalinmaz.

---

## 10. Onerilen Ilk Teknik Adimlar

Eger buradan devam edeceksek ilk 5 adim su olmali:

1. `RUN_MODE` kavramini ekle
2. `mock provider` tasarla
3. `fixtures/scenarios/` yapisini kur
4. ilk 3 fixture senaryosunu yaz:
   - python_cli
   - cpp_tool
   - web_dashboard
5. `--mock` ile pipeline'in uctan uca calistigini dogrula

Bu bes adimdan sonra proje cok daha rahat gelistirilir hale gelir.

---

## 11. Kisa Sonuc

Bu repo bugun artik "duzeltilmesi gereken kirik bir script" degil.

Bugunku durum:

- temel orchestration var
- dil-agnostik cekirdek var
- test tabani var
- cost visibility var
- public portfolyo temizligi yapildi

Bir sonraki buyuk kazanc:

**ucretsiz / dusuk maliyetli validation katmani**

Bu katman kurulmadan bu proje gelistirilebilir, ama pahali ve yavas olur.
Bu katman kuruldugunda ise hem kisisel arac hem de urun adayi olarak cok daha hizli buyur.

