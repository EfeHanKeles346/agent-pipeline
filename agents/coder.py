"""Coder Agent — Plan'a göre kod yazar, feedback'e göre düzeltir."""

from agents.base import BaseAgent


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="coder")

    def code(self, plan: str, memory: str = "", existing_files: str = "") -> str:
        """
        Planner'ın planına göre kod yaz.

        Args:
            plan: Planner agent'ın çıktısı
            memory: memory.md içeriği
            existing_files: Workspace'teki mevcut dosyaların içeriği

        Returns:
            Yazılan kod ve dosyalar
        """
        message = f"## Planner'ın Planı\n\n{plan}\n\n"

        if existing_files:
            message += f"{existing_files}\n\n---\n\n"

        message += (
            "Bu plana göre kodu yaz. "
            "Mevcut dosyalar varsa onlarla uyumlu çalış, gereksiz yere ezme. "
            "Tüm dosyaları tam olarak, eksiksiz üret."
        )
        return self.run(user_message=message, context=memory)

    def fix(self, previous_code: str, feedback: str, memory: str = "", existing_files: str = "") -> str:
        """
        Reviewer feedback'ine göre kodu düzelt.

        Args:
            previous_code: Önceki kodlama çıktısı
            feedback: Reviewer'ın feedback'i
            memory: memory.md içeriği
            existing_files: Workspace'teki mevcut dosyaların içeriği

        Returns:
            Düzeltilmiş kod
        """
        message = f"## Önceki Kod\n\n{previous_code}\n\n"
        message += f"## REVIEWER FEEDBACK\n\n{feedback}\n\n"

        if existing_files:
            message += f"{existing_files}\n\n---\n\n"

        message += (
            "Yukarıdaki feedback'e göre kodu düzelt. "
            "Sadece belirtilen sorunları çöz, çalışan kısımları bozma. "
            "Dosyaların tam içeriğini yaz."
        )
        return self.run(user_message=message, context=memory)
