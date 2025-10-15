import os
import json

# Try import groq; if not available, we'll fallback gracefully
try:
    from groq import Groq
    _HAS_GROQ = True
except Exception:
    _HAS_GROQ = False

class AIFeedback:
    def __init__(self):
        if not _HAS_GROQ:
            raise RuntimeError("Module 'groq' tidak ditemukan. Install 'groq' atau gunakan offline mode.")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY belum diatur di environment.")
        self.client = Groq(api_key=api_key)

    def request_fixed_code(self, code, language='python'):
        """
        Minta model memberikan versi kode yang sudah diperbaiki.
        Mengembalikan string (kode), atau None jika gagal.
        """
        system_prompt = (
            "Kamu adalah AI Code Fixer profesional. "
            "Tugasmu: perbaiki kode berikut agar bisa dijalankan tanpa error. "
            "Kembalikan hanya kode yang telah diperbaiki, tanpa penjelasan."
        )

        user_prompt = f"Bahasa: {language}\n\nKode asli:\n```\n{code}\n```\n\nBerikan hanya kode yang sudah diperbaiki."

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=8192
            )
            # Attempt to extract the assistant content
            content = response.choices[0].message.content
            if isinstance(content, dict):
                # Some SDKs may return structured message; stringify if needed
                content = json.dumps(content)
            fixed_code = content.strip()
            return fixed_code
        except Exception as e:
            raise RuntimeError(f"AI request failed: {e}")

