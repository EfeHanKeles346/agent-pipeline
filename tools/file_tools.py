"""
Dosya işlemleri — memory.md okuma, todolist yönetimi, log yazma, kod kaydetme, workspace okuma
"""

import os
import re
import json
from fnmatch import fnmatch
from datetime import datetime
import config

IGNORED_DIRS = {
    "node_modules", "__pycache__", ".git", ".next", ".vite",
    "dist", "build", ".cache", ".turbo", "coverage", ".nuxt",
    "target", "vendor", "bin", "obj", ".gradle", "out",
    "cmake-build-debug", "cmake-build-release",
}

IGNORED_DIR_PATTERNS = {
    "cmake-build-*",
}

IGNORED_FILES = {
    ".DS_Store", "Thumbs.db", "package-lock.json", "yarn.lock",
    "pnpm-lock.yaml",
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss",
    ".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".env", ".sh", ".bash", ".sql", ".graphql", ".svelte", ".vue",
    ".xml", ".csv", ".lock", ".config", ".mjs", ".cjs",
    ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
    ".go",
    ".rs",
    ".java", ".kt", ".kts", ".gradle",
    ".cs", ".csproj", ".sln",
    ".rb", ".php", ".swift", ".dart", ".zig",
    ".properties",
}

SPECIAL_TEXT_FILES = {
    "Makefile",
    "CMakeLists.txt",
    "Dockerfile",
    "Vagrantfile",
    "Gemfile",
    "go.mod",
    "go.sum",
}

CONFIG_FILENAMES = {
    "package.json",
    "tsconfig.json",
    "vite.config.ts",
    "tailwind.config.js",
    "webpack.config.js",
    "next.config.js",
    ".eslintrc.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "CMakeLists.txt",
    "Makefile",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Dockerfile",
    "Gemfile",
}

CONFIG_EXTENSIONS = {
    ".csproj",
    ".sln",
}


def _should_ignore_dir(dirname: str) -> bool:
    """Literal veya pattern tabanli ignore dizin kontrolu."""
    return dirname in IGNORED_DIRS or any(
        fnmatch(dirname, pattern) for pattern in IGNORED_DIR_PATTERNS
    )


def _is_workspace_text_file(filename: str) -> bool:
    """Workspace context'ine alinabilecek metin dosyasi mi?"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in TEXT_EXTENSIONS or filename in SPECIAL_TEXT_FILES


def _is_config_file(filename: str) -> bool:
    """Config dosyalarini context'te one al."""
    ext = os.path.splitext(filename)[1].lower()
    return filename in CONFIG_FILENAMES or ext in CONFIG_EXTENSIONS


def read_memory() -> str:
    """memory.md dosyasını oku. Yoksa boş döndür."""
    try:
        with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"  UYARI: {config.MEMORY_FILE} bulunamadı. Boş memory ile devam.")
        return ""


def read_todolist() -> list[dict]:
    """
    todolist.md dosyasını parse et.

    Format:
        - [ ] Task açıklaması
        - [x] Tamamlanmış task

    Returns:
        list[dict]: [{"task": str, "done": bool, "line": int}, ...]
    """
    try:
        with open(config.TODOLIST_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"\n todolist.md bulunamadı: {config.TODOLIST_FILE}\n"
            f" workspace/ klasörüne todolist.md oluştur.\n"
            f" Format:\n"
            f"   - [ ] İlk task\n"
            f"   - [ ] İkinci task\n"
        )

    tasks = []
    for i, line in enumerate(lines):
        # - [ ] task veya - [x] task formatını yakala
        match = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line.strip())
        if match:
            done = match.group(1).lower() == "x"
            task_text = match.group(2).strip()
            tasks.append({
                "task": task_text,
                "done": done,
                "line": i,
            })

    return tasks


def get_pending_tasks() -> list[dict]:
    """Tamamlanmamış task'ları döndür."""
    return [t for t in read_todolist() if not t["done"]]


def mark_task_done(task_text: str):
    """Todolist'te bir task'ı tamamlanmış olarak işaretle."""
    try:
        with open(config.TODOLIST_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # - [ ] task → - [x] task
        old = f"- [ ] {task_text}"
        new = f"- [x] {task_text}"

        if old in content:
            content = content.replace(old, new, 1)
            with open(config.TODOLIST_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Todolist güncellendi: {task_text}")
        else:
            print(f"  UYARI: Task bulunamadı todolist'te: {task_text}")

    except FileNotFoundError:
        print("  UYARI: todolist.md bulunamadı, güncelleme atlandı.")


def write_log(task: str, log_data: dict):
    """Bir task'ın çalışma logunu kaydet."""
    os.makedirs(config.LOGS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Task adından dosya-güvenli isim oluştur
    safe_task = re.sub(r"[^\w\s-]", "", task)[:50].strip().replace(" ", "_")
    log_file = os.path.join(config.LOGS_DIR, f"{timestamp}_{safe_task}.md")

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"# Task Log: {task}\n")
        f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if "plan" in log_data:
            f.write(f"## Planner Çıktısı\n\n{log_data['plan']}\n\n")

        if "code" in log_data:
            f.write(f"## Coder Çıktısı\n\n{log_data['code']}\n\n")

        if "reviews" in log_data:
            for i, review in enumerate(log_data["reviews"], 1):
                f.write(f"## Review #{i}\n\n```json\n{review}\n```\n\n")

        if "test" in log_data:
            f.write(f"## Tester Çıktısı\n\n```json\n{log_data['test']}\n```\n\n")

        if "commit" in log_data:
            f.write(f"## Commit Bilgisi\n\n```json\n{log_data['commit']}\n```\n\n")

        if "error" in log_data:
            f.write(f"## HATA\n\n{log_data['error']}\n\n")

    print(f"  Log kaydedildi: {log_file}")
    return log_file


def read_workspace_files(workspace_dir: str = None) -> str:
    """
    Workspace içindeki tüm kaynak dosyaları oku ve formatlanmış string döndür.
    Coder/Planner'a mevcut proje durumunu göstermek için kullanılır.

    Toplam context boyutu config.MAX_WORKSPACE_CONTEXT_CHARS ile sınırlandırılır.
    Config dosyaları (.json, .config.js/ts) öncelikli olarak eklenir.

    Args:
        workspace_dir: Taranacak dizin (default: config.WORKSPACE_DIR)

    Returns:
        Formatlanmış string: her dosyanın yolu ve içeriği
    """
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    if not os.path.exists(workspace_dir):
        return ""

    max_file_size = config.MAX_FILE_SIZE
    max_total = config.MAX_WORKSPACE_CONTEXT_CHARS

    # Dosyaları topla
    all_files = []
    for root, dirs, files in os.walk(workspace_dir):
        dirs[:] = [d for d in dirs if not _should_ignore_dir(d)]
        dirs.sort()

        for filename in sorted(files):
            if filename in IGNORED_FILES:
                continue
            if filename in ("memory.md", "todolist.md"):
                continue

            if not _is_workspace_text_file(filename):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, workspace_dir)

            try:
                size = os.path.getsize(full_path)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    if size > max_file_size:
                        content = f.read(max_file_size) + "\n... (dosya kırpıldı)"
                    else:
                        content = f.read()

                if content.strip():
                    # Config dosyalarını önceliklendir
                    is_config = _is_config_file(filename)
                    all_files.append((rel_path, content, is_config))
            except (OSError, UnicodeDecodeError):
                continue

    if not all_files:
        return ""

    # Config dosyalarını öne al
    all_files.sort(key=lambda x: (not x[2], x[0]))

    files_content = []
    total_chars = 0
    file_count = 0
    skipped = 0

    for rel_path, content, _is_config in all_files:
        entry = f"### `{rel_path}`\n```\n{content}\n```"
        if total_chars + len(entry) > max_total:
            skipped += 1
            continue
        files_content.append(entry)
        total_chars += len(entry)
        file_count += 1

    header = f"## Mevcut Workspace Dosyaları ({file_count} dosya"
    if skipped:
        header += f", {skipped} dosya context limiti nedeniyle atlandı"
    header += ")\n\n"
    return header + "\n\n".join(files_content)


def save_code_files(coder_output: str, workspace_dir: str = None):
    """
    Coder agent'ın çıktısından dosyaları ayıkla ve diske kaydet.
    Satır satır parse eder — nested code block'lara karşı dayanıklıdır.

    Coder çıktı formatı:
        ### `path/to/file.ext`
        ```lang
        code content
        ```
    """
    if workspace_dir is None:
        workspace_dir = config.WORKSPACE_DIR

    saved_files = []
    current_file = None
    current_content = []
    in_code_block = False

    lines = coder_output.split("\n")

    for index, line in enumerate(lines):
        # Dosya başlığını yakala: ### `filepath`
        file_match = re.match(r"^###\s*`([^`]+)`", line)
        if file_match and not in_code_block:
            # Önceki dosyayı kaydet
            if current_file and current_content:
                _save_single_file(current_file, current_content, workspace_dir, saved_files)
            current_file = file_match.group(1).strip()
            current_content = []
            continue

        # Code block başlangıcı (```lang veya ```)
        if re.match(r"^```\w*$", line.strip()) and not in_code_block:
            in_code_block = True
            continue

        # Code block bitişi
        if line.strip() == "```" and in_code_block:
            next_nonempty = ""
            for future_line in lines[index + 1:]:
                stripped = future_line.strip()
                if stripped:
                    next_nonempty = stripped
                    break

            # İçerikteki fenced markdown bloklarını koru; yalnızca
            # yeni dosya/section başlangıcından önceki fence outer block'tur.
            if next_nonempty and not (
                next_nonempty.startswith("### `") or next_nonempty.startswith("## ")
            ):
                current_content.append(line)
                continue

            in_code_block = False
            continue

        # İçerik toplama
        if in_code_block and current_file:
            current_content.append(line)

    # Son dosyayı kaydet
    if current_file and current_content:
        _save_single_file(current_file, current_content, workspace_dir, saved_files)

    if not saved_files:
        print("  UYARI: Coder çıktısından dosya ayıklanamadı.")
        print("  (Coder çıktı formatı ### `filepath` ... ``` olmalı)")

    return saved_files


def _save_single_file(filepath: str, content_lines: list, workspace_dir: str, saved_files: list):
    """Tek bir dosyayı diske kaydet."""
    full_path = os.path.join(workspace_dir, filepath)
    full_path = os.path.normpath(full_path)

    if not full_path.startswith(os.path.normpath(workspace_dir)):
        print(f"  UYARI: Güvenlik — workspace dışına yazma engellendi: {filepath}")
        return

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    content = "\n".join(content_lines).strip() + "\n"
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    saved_files.append(full_path)
    print(f"  Dosya kaydedildi: {full_path}")


# ============================================
# PIPELINE STATE PERSISTENCE
# ============================================

STATE_FILE = os.path.join(config.PIPELINE_DIR, ".pipeline_state.json")


def save_state(task_text: str, step: str, data: dict):
    """Pipeline durumunu kaydet — yarıda kalan task kaldığı yerden devam edebilsin."""
    state = {
        "task": task_text,
        "step": step,
        "attempt": data.get("attempt", 1),
        "plan": data.get("plan"),
        "code": data.get("code"),
        "timestamp": datetime.now().isoformat(),
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_state(task_text: str) -> dict | None:
    """Kaydedilmiş pipeline durumunu yükle."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("task") == task_text:
            return state
    except (json.JSONDecodeError, OSError):
        pass
    return None


def clear_state():
    """Pipeline durumunu temizle."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


# ============================================
# MEMORY.MD OTOMATİK GÜNCELLEME
# ============================================

def update_memory(task_text: str, files_created: list, files_modified: list = None):
    """Her task tamamlandığında memory.md'ye otomatik bilgi ekle."""
    try:
        with open(config.MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## Task Tamamlandı: {task_text}\n")
            f.write(f"- Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            if files_created:
                # Workspace dir prefix'ini kaldır
                workspace = os.path.normpath(config.WORKSPACE_DIR)
                rel_files = []
                for fp in files_created:
                    fp_norm = os.path.normpath(fp)
                    if fp_norm.startswith(workspace):
                        rel_files.append(os.path.relpath(fp_norm, workspace))
                    else:
                        rel_files.append(fp)
                f.write(f"- Dosyalar: {', '.join(rel_files)}\n")
    except OSError as e:
        print(f"  UYARI: Memory güncellenemedi: {e}")
