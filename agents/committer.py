"""Committer Agent — Tamamlanan task'ı memory için özetler."""

from agents.base import BaseAgent


class CommitterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="committer")

    def summarize(self, task: str, code: str, review_summary: str, files_changed: list[str] | None = None) -> dict:
        """
        Tamamlanan task için memory girdisi üret.

        Args:
            task: Orijinal task açıklaması
            code: Son hali ile kod
            review_summary: Reviewer'ın son değerlendirmesi
            files_changed: Değişen dosyaların göreli yolları

        Returns:
            dict: {"memory_entry": str, "important_patterns": list[str]}
        """
        changed_files_text = ", ".join(files_changed or []) if files_changed else "bilinmiyor"
        message = (
            f"## Tamamlanan Task\n\n{task}\n\n"
            f"## Yazılan Kod (özet)\n\n{code[:2000]}\n\n"
            f"## Review Özeti\n\n{review_summary}\n\n"
            f"## Değişen Dosyalar\n\n{changed_files_text}\n\n"
            "Bu task için memory.md'ye eklenecek kısa ama yararlı bir özet üret. "
            "JSON formatında yanıt ver."
        )

        default = {
            "memory_entry": (
                f"## Task Tamamlandı: {task}\n"
                f"- Özet: Task tamamlandı.\n"
                f"- Reviewer özeti: {review_summary or 'Detay parse edilemedi.'}\n"
            ),
            "important_patterns": [],
        }
        return self.run_json(user_message=message, default=default)
