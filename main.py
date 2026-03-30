"""
Multi-Agent Pipeline — Ana Orchestrator
========================================

Kullanım:
    python main.py              # Tüm pending task'ları çalıştır
    python main.py --task 1     # Sadece 1. pending task'ı çalıştır
    python main.py --list       # Task listesini göster
    python main.py --dry-run    # Agent çağırmadan akışı test et
    python main.py --no-install # Otomatik dependency kurulumunu atla
    python main.py --no-server  # Otomatik dev server başlatmayı atla

Özelleştirme:
    1. workspace/todolist.md → görevlerini yaz
    2. workspace/memory.md → proje bağlamını yaz
    3. prompts/*.md → system prompt'ları düzenle
    4. config.py → model, retry sayısı, yollar
"""

import sys
import json
import time
import argparse
from datetime import datetime

import config
from agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent, CommitterAgent
from tools.file_tools import (
    read_memory,
    read_workspace_files,
    get_pending_tasks,
    mark_task_done,
    write_log,
    save_code_files,
    save_state,
    load_state,
    clear_state,
    update_memory,
)
from tools.shell_tools import (
    auto_install_dependencies,
    start_dev_server,
    stop_dev_server,
    detect_project_type,
    run_command,
)


def print_header():
    """Başlangıç banner'ı."""
    print("\n" + "=" * 60)
    print("  MULTI-AGENT PIPELINE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def print_task_list(tasks: list[dict]):
    """Task listesini göster."""
    print("\n  TASK LİSTESİ")
    print("  " + "-" * 40)
    for i, t in enumerate(tasks, 1):
        status = "DONE" if t["done"] else "TODO"
        icon = "  [x]" if t["done"] else "  [ ]"
        print(f"  {icon} {i}. {t['task']}")
    print()


def run_single_task(
    task_info: dict,
    task_number: int,
    total_tasks: int,
    memory: str,
    dry_run: bool = False,
    auto_install: bool = True,
):
    """
    Tek bir task için tam pipeline döngüsünü çalıştır.

    Akış: Planner → Coder ⇄ Reviewer → (Tester) → (Committer) → (Install)
    """
    task_text = task_info["task"]

    print(f"\n{'#'*60}")
    print(f"  TASK {task_number}/{total_tasks}: {task_text}")
    print(f"{'#'*60}")

    if dry_run:
        print("  [DRY RUN] Agent çağrıları atlanıyor.")
        return True

    log_data = {}

    try:
        # ─────────────────────────────────────
        # STATE RECOVERY — Yarıda kalan task'ı devam ettir
        # ─────────────────────────────────────
        saved_state = load_state(task_text)
        if saved_state:
            print(f"  Kaldığı yerden devam ediliyor (adım: {saved_state['step']})")

        # ─────────────────────────────────────
        # WORKSPACE DOSYALARINI OKU
        # ─────────────────────────────────────
        existing_files = ""
        if config.SEND_WORKSPACE_CONTEXT:
            print("\n  Workspace dosyaları okunuyor...")
            existing_files = read_workspace_files()
            if existing_files:
                file_count = existing_files.split("\n")[0] if existing_files else "0"
                print(f"  {file_count}")
            else:
                print("  Workspace boş (ilk task)")

        # ─────────────────────────────────────
        # ADIM 1: PLANNER
        # ─────────────────────────────────────
        if saved_state and saved_state.get("plan"):
            print("\n  ADIM 1/5: Planlama (state'den yüklendi)")
            plan = saved_state["plan"]
        else:
            print("\n  ADIM 1/5: Planlama")
            planner = PlannerAgent()
            plan = planner.plan(task=task_text, memory=memory, existing_files=existing_files)
        log_data["plan"] = plan
        save_state(task_text, "planner", {"plan": plan})

        # ─────────────────────────────────────
        # ADIM 2-3: CODER + REVIEWER DÖNGÜSÜ
        # ─────────────────────────────────────
        coder = CoderAgent()
        reviewer = ReviewerAgent()

        code = saved_state.get("code") if saved_state else None
        review_result = None
        reviews = []
        start_attempt = saved_state.get("attempt", 1) if saved_state and saved_state.get("code") else 1

        for attempt in range(start_attempt, config.MAX_REVIEW_ATTEMPTS + 1):
            print(f"\n  ADIM 2/5: Kodlama (deneme {attempt}/{config.MAX_REVIEW_ATTEMPTS})")

            if config.SEND_WORKSPACE_CONTEXT and attempt > 1:
                existing_files = read_workspace_files()

            if attempt == start_attempt and code:
                print("  (state'den yüklendi)")
            elif attempt == 1:
                code = coder.code(plan=plan, memory=memory, existing_files=existing_files)
            else:
                feedback_text = json.dumps(review_result, indent=2, ensure_ascii=False)
                code = coder.fix(
                    previous_code=code,
                    feedback=feedback_text,
                    memory=memory,
                    existing_files=existing_files,
                )

            saved = save_code_files(code)
            save_state(task_text, "coder", {"plan": plan, "code": code, "attempt": attempt})

            if config.SEND_WORKSPACE_CONTEXT:
                existing_files = read_workspace_files()

            print(f"\n  ADIM 3/5: Code Review (tur {attempt})")
            review_result = reviewer.review(code=code, plan=plan, existing_files=existing_files)
            reviews.append(json.dumps(review_result, indent=2, ensure_ascii=False))

            approved = review_result.get("approved", False)
            score = review_result.get("score", "?")
            summary = review_result.get("summary", "")

            print(f"  Review sonucu: {'ONAYLANDI' if approved else 'REDDEDİLDİ'} (skor: {score}/10)")
            print(f"  Özet: {summary}")

            if approved:
                print(f"\n  Kod {attempt}. denemede onaylandı!")
                break

            if attempt == config.MAX_REVIEW_ATTEMPTS:
                print(f"\n  UYARI: {config.MAX_REVIEW_ATTEMPTS} denemede onaylanamadı!")
                print("  Son haliyle devam ediliyor...")

        log_data["code"] = code
        log_data["reviews"] = reviews

        # ─────────────────────────────────────
        # ADIM 4: TESTER (opsiyonel)
        # ─────────────────────────────────────
        if config.ENABLE_TESTER:
            print("\n  ADIM 4/5: Test")
            tester = TesterAgent()
            test_result = tester.test(code=code, existing_files=existing_files)
            log_data["test"] = json.dumps(test_result, indent=2, ensure_ascii=False)

            passed = test_result.get("passed", True)
            print(f"  Test sonucu: {'PASS' if passed else 'FAIL'}")

            if not passed:
                print("  UYARI: Test başarısız. Log'a kaydedildi.")
        else:
            print("\n  ADIM 4/5: Test (devre dışı, atlanıyor)")

        # ─────────────────────────────────────
        # BUILD TEST — Gerçek build kontrolü
        # ─────────────────────────────────────
        if auto_install and detect_project_type() == "node":
            print("\n  BUILD TEST: npm run build çalıştırılıyor...")
            build_result = run_command("npm run build", timeout=120, silent=True)
            if build_result["success"]:
                print("  Build başarılı!")
                log_data["build"] = "success"
            else:
                print("  BUILD UYARI: Build başarısız (log'a kaydedildi)")
                log_data["build"] = build_result.get("stderr", "")[:2000]

        # ─────────────────────────────────────
        # ADIM 5: COMMITTER (opsiyonel)
        # ─────────────────────────────────────
        if config.ENABLE_COMMITTER:
            print("\n  ADIM 5/5: Commit & Güncelleme")
            committer = CommitterAgent()
            commit_result = committer.commit(
                task=task_text,
                code=code,
                review_summary=review_result.get("summary", ""),
            )
            log_data["commit"] = json.dumps(commit_result, indent=2, ensure_ascii=False)

            commit_msg = commit_result.get("commit_message", "")
            print(f"  Commit mesajı: {commit_msg[:80]}")
        else:
            print("\n  ADIM 5/5: Commit (devre dışı, atlanıyor)")

        # ─────────────────────────────────────
        # DEPENDENCY KURULUMU (otomatik)
        # ─────────────────────────────────────
        if auto_install:
            install_result = auto_install_dependencies()
            if install_result:
                log_data["install"] = {
                    "success": install_result["success"],
                    "stderr": install_result.get("stderr", "")[:500],
                }
                if not install_result["success"]:
                    print("  UYARI: Dependency kurulumu başarısız!")

        # Task'ı tamamla
        mark_task_done(task_text)

        # Memory'yi güncelle
        update_memory(task_text, saved)

        # Log kaydet
        write_log(task_text, log_data)

        # State temizle
        clear_state()

        print(f"\n  TASK TAMAMLANDI: {task_text}")
        return True

    except Exception as e:
        print(f"\n  HATA: {e}")
        log_data["error"] = str(e)
        write_log(task_text, log_data)
        return False


def main():
    """Ana giriş noktası."""
    parser = argparse.ArgumentParser(description="Multi-Agent Pipeline")
    parser.add_argument("--task", type=int, help="Sadece N. pending task'ı çalıştır")
    parser.add_argument("--list", action="store_true", help="Task listesini göster")
    parser.add_argument("--dry-run", action="store_true", help="Agent çağırmadan test et")
    parser.add_argument("--no-install", action="store_true", help="Otomatik dependency kurulumunu atla")
    parser.add_argument("--no-server", action="store_true", help="Otomatik dev server başlatmayı atla")
    args = parser.parse_args()

    print_header()

    # API key kontrolü
    if not config.API_KEY and not args.list:
        print("\n  HATA: API Key bulunamadı!")
        print("  Çözüm 1: export ANTHROPIC_API_KEY='sk-ant-xxxxx'")
        print("  Çözüm 2: config.py dosyasında API_KEY'i ayarla")
        sys.exit(1)

    # Otomasyon flag'larını belirle
    do_install = config.AUTO_INSTALL and not args.no_install and not args.dry_run
    do_server = config.AUTO_DEV_SERVER and not args.no_server and not args.dry_run

    # Konfigürasyonu göster
    print(f"\n  Workspace:    {config.WORKSPACE_DIR}")
    print(f"  Todolist:     {config.TODOLIST_FILE}")
    print(f"  Memory:       {config.MEMORY_FILE}")
    print(f"  Tester:       {'Aktif' if config.ENABLE_TESTER else 'Pasif'}")
    print(f"  Committer:    {'Aktif' if config.ENABLE_COMMITTER else 'Pasif'}")
    print(f"  Max retry:    {config.MAX_REVIEW_ATTEMPTS}")
    print(f"  Auto install: {'Aktif' if do_install else 'Pasif'}")
    print(f"  Dev server:   {'Aktif' if do_server else 'Pasif'}")
    print(f"  Workspace ctx:{'Aktif' if config.SEND_WORKSPACE_CONTEXT else 'Pasif'}")

    # Modelleri göster
    print("\n  Modeller:")
    for agent_name, model in config.MODELS.items():
        print(f"    {agent_name:12s} → {model}")

    # Task'ları oku
    try:
        from tools.file_tools import read_todolist
        all_tasks = read_todolist()
    except FileNotFoundError as e:
        print(f"\n{e}")
        sys.exit(1)

    print_task_list(all_tasks)

    if args.list:
        sys.exit(0)

    # Pending task'ları al
    pending = get_pending_tasks()
    if not pending:
        print("  Tüm task'lar tamamlanmış! Yeni task ekle: workspace/todolist.md")
        sys.exit(0)

    print(f"  {len(pending)} adet bekleyen task var.\n")

    # Memory oku
    memory = read_memory()
    if memory:
        print(f"  Memory yüklendi ({len(memory)} karakter)")
    else:
        print("  Memory boş (workspace/memory.md)")

    # Tek task mı, hepsi mi?
    if args.task:
        if args.task < 1 or args.task > len(pending):
            print(f"  HATA: --task {args.task} geçersiz. 1-{len(pending)} arası olmalı.")
            sys.exit(1)
        tasks_to_run = [pending[args.task - 1]]
    else:
        tasks_to_run = pending

    # Pipeline'ı çalıştır
    results = []
    for i, task_info in enumerate(tasks_to_run, 1):
        if i > 1:
            cooldown = config.TASK_COOLDOWN_SECONDS
            print(f"\n  {cooldown}s bekleniyor (rate limit koruması)...")
            time.sleep(cooldown)

        success = run_single_task(
            task_info=task_info,
            task_number=i,
            total_tasks=len(tasks_to_run),
            memory=memory,
            dry_run=args.dry_run,
            auto_install=do_install,
        )
        results.append({"task": task_info["task"], "success": success})

    # Sonuç özeti
    print("\n" + "=" * 60)
    print("  PIPELINE RAPORU")
    print("=" * 60)

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    for r in results:
        icon = "[OK]" if r["success"] else "[XX]"
        print(f"  {icon} {r['task']}")

    print(f"\n  Toplam: {success_count} başarılı, {fail_count} başarısız")
    print(f"  Log'lar: {config.LOGS_DIR}/")

    # ─────────────────────────────────────
    # DEV SERVER BAŞLAT
    # ─────────────────────────────────────
    if do_server and success_count > 0:
        project_type = detect_project_type()
        if project_type != "unknown":
            print("\n" + "-" * 60)
            print("  DEV SERVER")
            print("-" * 60)
            server_result = start_dev_server()
            print(f"  {server_result['message']}")
            if server_result["success"]:
                print("\n  Tarayıcıda aç:")
                if project_type == "node":
                    print("    http://localhost:5173  (Vite)")
                    print("    http://localhost:3000  (Next.js / CRA)")
                else:
                    print("    http://localhost:5000  (Flask)")
                    print("    http://localhost:8000  (Django)")
                print("\n  Durdurmak için: Ctrl+C")

    print("=" * 60 + "\n")

    # Dev server çalışıyorsa bekle
    if do_server and success_count > 0:
        try:
            from tools.shell_tools import _dev_server_process
            if _dev_server_process and _dev_server_process.poll() is None:
                print("  Dev server çalışıyor. Çıkmak için Ctrl+C...\n")
                _dev_server_process.wait()
        except KeyboardInterrupt:
            print("\n")
            stop_dev_server()
            print("  Pipeline sonlandırıldı.")


if __name__ == "__main__":
    main()
