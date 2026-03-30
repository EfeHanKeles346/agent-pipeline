"""Tester Agent — Kodu analiz eder, test senaryoları önerir."""

from agents.base import BaseAgent


class TesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="tester")

    def test(self, code: str, existing_files: str = "") -> dict:
        """
        Kodu analiz et, syntax ve mantık kontrolü yap.

        Args:
            code: Coder agent'ın çıktısı
            existing_files: Workspace'teki mevcut dosyaların içeriği

        Returns:
            dict: {"passed": bool, "issues": list, ...}
        """
        message = f"## Kod\n\n{code}\n\n"

        if existing_files:
            message += (
                f"{existing_files}\n\n---\n\n"
                "NOT: Yukarıdaki 'Mevcut Workspace Dosyaları' bölümü diskte gerçekten var olan dosyaları gösterir. "
                "Import'ları ve tanımları kontrol ederken bu dosyaları da dikkate al.\n\n"
            )

        message += (
            "Bu kodu analiz et. Syntax hatası, import eksikliği, "
            "tip uyumsuzluğu var mı? JSON formatında yanıt ver."
        )

        default = {
            "passed": True,
            "syntax_check": "unknown",
            "issues": [],
            "test_commands": [],
            "summary": "Yanıt parse edilemedi, test atlandı.",
        }
        return self.run_json(user_message=message, default=default)
