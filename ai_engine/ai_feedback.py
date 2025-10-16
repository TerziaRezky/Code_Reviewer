import os
import json

# Try import groq; if not available, we'll fallback gracefully
try:
    from groq import Groq
    _HAS_GROQ = True
    print("✅ Groq module berhasil diimport")
except ImportError as e:
    _HAS_GROQ = False
    print(f"⚠️ Groq module tidak ditemukan: {e}")

class AIFeedback:
    def __init__(self):
        self.is_available = False
        self.error_message = ""
        
        if not _HAS_GROQ:
            self.error_message = "Module 'groq' tidak ditemukan. Install dengan: pip install groq"
            print(self.error_message)
            return
            
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            self.error_message = "GROQ_API_KEY belum diatur di environment variables."
            print(self.error_message)
            return
            
        try:
            self.client = Groq(api_key=api_key)
            self.is_available = True
            print("✅ AIFeedback berhasil diinisialisasi")
        except Exception as e:
            self.error_message = f"Gagal inisialisasi Groq client: {e}"
            print(self.error_message)

    def request_fixed_code(self, code, language='python'):
        """
        Minta model memberikan versi kode yang sudah diperbaiki.
        Mengembalikan string (kode), atau None jika gagal.
        """
        if not self.is_available:
            raise RuntimeError(self.error_message)
        
        system_prompt = (
            "Kamu adalah AI Code Fixer profesional. "
            "Tugasmu: perbaiki kode berikut agar bisa dijalankan tanpa error. "
            "Kembalikan hanya kode yang telah diperbaiki, tanpa penjelasan, tanpa markdown formatting."
        )

        user_prompt = f"Bahasa: {language}\n\nKode asli:\n```{language}\n{code}\n```\n\nBerikan hanya kode yang sudah diperbaiki tanpa penjelasan apapun."

        models_to_try = ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
        
        for model in models_to_try:
            try:
                print(f"🔄 Mencoba model: {model}")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=8192
                )
                
                content = response.choices[0].message.content
                fixed_code = content.strip()
                
                # Clean up code blocks
                if fixed_code.startswith(f"```{language}"):
                    fixed_code = fixed_code[len(f"```{language}"):]
                elif fixed_code.startswith("```"):
                    fixed_code = fixed_code[3:]
                
                if fixed_code.endswith("```"):
                    fixed_code = fixed_code[:-3]
                
                fixed_code = fixed_code.strip()
                
                if fixed_code and len(fixed_code) > 10:
                    print(f"✅ Berhasil mendapatkan fixed code dari {model}")
                    return fixed_code
                    
            except Exception as e:
                print(f"❌ Model {model} gagal: {e}")
                continue
        
        raise RuntimeError("Semua model AI gagal memberikan respons")

    def check_availability(self):
        """Cek apakah AI service available"""
        return self.is_available, self.error_message if not self.is_available else "AI service ready"
