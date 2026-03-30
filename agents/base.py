"""
Base Agent — Tüm agent'ların temel sınıfı
Her agent bu sınıftan türer, kendi prompt'unu ve modelini alır.
"""

import os
import time
import json
import anthropic
import config

MAX_API_RETRIES = 3
INITIAL_BACKOFF = 5  # saniye


class BaseAgent:
    """Temel agent sınıfı. Her agent bu sınıfı extend eder."""

    def __init__(self, name: str, model: str | None = None):
        self.name = name
        self.model = model or config.MODELS.get(name, "claude-sonnet-4-20250514")
        self.system_prompt = self._load_prompt()
        self.client = anthropic.Anthropic(api_key=config.API_KEY)
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_api_calls = 0

    def _load_prompt(self) -> str:
        """prompts/ klasöründen system prompt'u oku."""
        prompt_file = os.path.join(config.PROMPTS_DIR, f"{self.name}.md")
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"System prompt bulunamadı: {prompt_file}\n"
                f"prompts/{self.name}.md dosyasını oluştur."
            )

    def run(self, user_message: str, context: str = "") -> str:
        """
        Agent'ı çalıştır. Rate limit ve server hatalarında exponential backoff ile retry yapar.

        Args:
            user_message: Agent'a gönderilecek ana mesaj
            context: Ek bağlam (memory, önceki çıktılar vs.)

        Returns:
            Agent'ın yanıtı (string)
        """
        full_message = ""
        if context:
            full_message += f"## Proje Bağlamı\n\n{context}\n\n---\n\n"
        full_message += user_message

        print(f"\n{'='*60}")
        print(f"  {self.name.upper()} agent çalışıyor... (model: {self.model})")
        print(f"{'='*60}")

        for attempt in range(MAX_API_RETRIES):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=config.MAX_TOKENS,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": full_message}
                    ],
                )

                result = response.content[0].text

                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                self.total_api_calls += 1
                print(f"  Tokens: {input_tokens} input + {output_tokens} output")
                print(f"  {self.name.upper()} tamamlandı.")

                return result

            except anthropic.AuthenticationError:
                raise RuntimeError(
                    "\n API KEY HATASI!\n"
                    " .env dosyasına ANTHROPIC_API_KEY ekle veya:\n"
                    " export ANTHROPIC_API_KEY='sk-ant-xxxxx'\n"
                )
            except anthropic.RateLimitError:
                wait = INITIAL_BACKOFF * (2 ** attempt)
                print(f"  Rate limit — {wait}s bekleniyor (deneme {attempt + 1}/{MAX_API_RETRIES})")
                time.sleep(wait)
            except anthropic.APIStatusError as e:
                if e.status_code >= 500:
                    wait = INITIAL_BACKOFF * (2 ** attempt)
                    print(f"  Server hatası ({e.status_code}) — {wait}s bekleniyor (deneme {attempt + 1}/{MAX_API_RETRIES})")
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"\n {self.name} API hatası ({e.status_code}): {e}")
            except Exception as e:
                raise RuntimeError(f"\n {self.name} agent hatası: {e}")

        raise RuntimeError(
            f"\n {self.name}: {MAX_API_RETRIES} deneme sonrası API'ye ulaşılamadı.\n"
            " Rate limit devam ediyor — birkaç dakika bekleyip tekrar dene.\n"
        )

    def run_json(self, user_message: str, context: str = "", default: dict = None) -> dict:
        """Agent'ı çalıştır ve JSON yanıtı parse et."""
        raw = self.run(user_message, context)
        return self._parse_json_response(raw, default or {})

    def _parse_json_response(self, response: str, default: dict) -> dict:
        """JSON yanıtı parse et. Parse edilemezse default döndür."""
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, IndexError):
            print(f"  UYARI: {self.name} yanıtı JSON parse edilemedi.")
            return {**default, "raw_response": response}

    def reload_prompt(self):
        """System prompt'u dosyadan tekrar yükle (hot reload)."""
        self.system_prompt = self._load_prompt()
        print(f"  {self.name} prompt'u yeniden yüklendi.")
