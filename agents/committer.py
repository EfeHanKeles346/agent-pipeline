"""Committer Agent — Git commit mesajı üretir, todolist günceller."""

from agents.base import BaseAgent


class CommitterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="committer")

    def commit(self, task: str, code: str, review_summary: str) -> dict:
        """
        Tamamlanan task için commit bilgisi üret.

        Args:
            task: Orijinal task açıklaması
            code: Son hali ile kod
            review_summary: Reviewer'ın son değerlendirmesi

        Returns:
            dict: {"commit_message": str, "todolist_update": dict, "log_entry": str}
        """
        message = (
            f"## Tamamlanan Task\n\n{task}\n\n"
            f"## Yazılan Kod (özet)\n\n{code[:2000]}\n\n"
            f"## Review Özeti\n\n{review_summary}\n\n"
            "Bu task için commit mesajı, todolist güncellemesi ve "
            "log kaydı üret. JSON formatında yanıt ver."
        )

        default = {
            "commit_message": "feat: Task tamamlandı",
            "todolist_update": {"task": "unknown", "status": "done"},
            "log_entry": "Task tamamlandı (detay parse edilemedi).",
        }
        return self.run_json(user_message=message, default=default)
