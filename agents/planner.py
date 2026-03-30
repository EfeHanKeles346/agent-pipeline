"""Planner Agent — Task'ı analiz eder, coding prompt üretir."""

from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="planner")

    def plan(self, task: str, memory: str = "", existing_files: str = "") -> str:
        """
        Bir task için implementasyon planı üret.

        Args:
            task: Todolist'ten gelen task açıklaması
            memory: memory.md içeriği
            existing_files: Workspace'teki mevcut dosyaların içeriği

        Returns:
            Planlama çıktısı + coding prompt
        """
        message = f"## Task\n\n{task}\n\n"

        if existing_files:
            message += f"{existing_files}\n\n---\n\n"

        message += (
            "Bu task için detaylı bir implementasyon planı ve "
            "Coder agent'a verilecek bir coding prompt üret."
        )
        return self.run(user_message=message, context=memory)
