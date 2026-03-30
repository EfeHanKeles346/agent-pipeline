"""Reviewer Agent — Kodu inceler, onaylar veya reddeder."""

from agents.base import BaseAgent


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="reviewer")

    def review(self, code: str, plan: str, existing_files: str = "") -> dict:
        """
        Kodu incele ve değerlendir.

        Args:
            code: Coder agent'ın çıktısı
            plan: Orijinal plan (uyum kontrolü için)
            existing_files: Workspace'teki tüm dosyaların içeriği

        Returns:
            dict: {"approved": bool, "score": int, "summary": str, "issues": list, ...}
        """
        message = f"## Orijinal Plan\n\n{plan}\n\n"
        message += f"## Coder'ın Son Çıktısı\n\n{code}\n\n"

        if existing_files:
            message += (
                f"{existing_files}\n\n---\n\n"
                "NOT: Coder sadece değişen/yeni dosyaları çıktı olarak verir. "
                "Projenin tamamını değerlendirmek için yukarıdaki 'Mevcut Workspace Dosyaları' bölümüne bak. "
                "Diskte zaten var olan dosyaları eksik sayma.\n\n"
            )

        message += "Bu kodu incele. Plana uygun mu? Hatalar var mı? JSON formatında yanıt ver."

        default = {
            "approved": False,
            "score": 0,
            "summary": "Yanıt parse edilemedi, tekrar deneyin.",
            "issues": [
                {
                    "severity": "critical",
                    "file": "unknown",
                    "description": "Reviewer yanıtı parse edilemedi",
                    "fix": "Pipeline tekrar çalıştırılmalı",
                }
            ],
            "positives": [],
        }
        return self.run_json(user_message=message, default=default)
