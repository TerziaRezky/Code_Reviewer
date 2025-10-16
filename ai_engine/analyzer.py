import ast
import re
import os

# Try import groq; if not available, AI features will be disabled
try:
    from groq import Groq
    _HAS_GROQ = True
    print("✅ Groq module berhasil diimport di analyzer")
except ImportError:
    _HAS_GROQ = False
    print("⚠️ Groq tidak tersedia di analyzer - AI features dinonaktifkan")

class CodeAnalyzer:
    def __init__(self):
        # Inisialisasi hasil analisis
        self.syntax_errors = []
        self.style_issues = []
        self.efficiency_suggestions = []
        self.improvement_suggestions = []
        
        # Inisialisasi klien Groq hanya jika tersedia
        self.client = None
        if _HAS_GROQ:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.client = Groq(api_key=api_key)
                    print("✅ Groq client berhasil diinisialisasi di analyzer")
                except Exception as e:
                    print(f"⚠️ Gagal inisialisasi Groq client: {e}")
            else:
                print("⚠️ GROQ_API_KEY tidak ditemukan - AI features dinonaktifkan")
    
    def analyze_code(self, code, language='python'):
        """
        Analisis kode berdasarkan bahasa pemrograman
        """
        # Reset hasil sebelumnya
        self.syntax_errors = []
        self.style_issues = []
        self.efficiency_suggestions = []
        self.improvement_suggestions = []
        
        # Analisis berdasarkan bahasa
        if language == 'python':
            return self._analyze_python(code)
        elif language == 'javascript':
            return self._analyze_javascript(code)
        elif language == 'cpp':
            return self._analyze_cpp(code)
        else:
            return {
                'syntax_errors': ['❌ Bahasa tidak didukung'],
                'style_issues': ['Pilih Python, JavaScript, atau C++'],
                'efficiency_suggestions': [],
                'improvement_suggestions': []
            }
    
    def _analyze_python(self, code):
        """Analisis kode Python dengan deteksi error yang lebih baik"""
        self._check_python_syntax(code)
        self._check_python_style(code)
        self._check_python_efficiency(code)
        self._suggest_python_improvements(code)
        return self._format_results()
    
    def _check_python_syntax(self, code):
        """Cek sintaks Python dengan detail"""
        try:
            ast.parse(code)
            self._check_python_runtime_issues(code)
        except SyntaxError as e:
            error_msg = f"❌ Syntax Error: {e.msg}"
            if e.lineno:
                error_msg += f" pada baris {e.lineno}"
            if e.offset:
                error_msg += f", kolom {e.offset}"
            self.syntax_errors.append(error_msg)
        except Exception as e:
            self.syntax_errors.append(f"❌ Error parsing: {str(e)}")
    
    def _check_python_runtime_issues(self, code):
        """Cek kemungkinan error runtime"""
        lines = code.split('\n')
        defined_vars = set()

        for line in lines:
            match = re.search(r'^\s*(\w+)\s*=', line)
            if match:
                defined_vars.add(match.group(1))
        
        for i, line in enumerate(lines, 1):
            matches = re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?![\[\(\.])', line)
            for match in matches:
                var_name = match.group(1)
                if (var_name not in defined_vars and 
                    var_name not in ['print', 'range', 'len', 'def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 'return', 'True', 'False', 'None'] and
                    re.match(r'^[a-zA-Z_]', var_name)):
                    self.syntax_errors.append(f"⚠️ Variabel '{var_name}' mungkin belum didefinisikan (baris {i})")
                    break
    
    def _check_python_style(self, code):
        """Analisis gaya penulisan Python"""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                self.style_issues.append(f"📏 Baris {i}: Terlalu panjang ({len(line)} karakter)")
        
        if '\t' in code:
            self.style_issues.append("🎨 Gunakan spasi (4) bukan tab")
        
        variable_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        variables = re.findall(variable_pattern, code)
        for var in variables:
            if not var.startswith('_') and not var.islower() and not re.match(r'^[A-Z][A-Z0-9_]*$', var):
                self.style_issues.append(f"📝 Variabel '{var}' sebaiknya menggunakan snake_case")
        
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        functions = re.findall(function_pattern, code)
        for func in functions:
            if not func.replace('_', '').islower():
                self.style_issues.append(f"📝 Function '{func}' sebaiknya menggunakan snake_case")
    
    def _check_python_efficiency(self, code):
        """Analisis efisiensi kode Python"""
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if 'for i in range(len(' in line and '[' in line:
                self.efficiency_suggestions.append(f"⚡ Baris {i}: Gunakan enumerate() daripada range(len())")
                break
        
        if 'for' in code and '+=' in code and ('"' in code or "'" in code):
            self.efficiency_suggestions.append("⚡ Gunakan list + join() untuk concatenation string dalam loop")
    
    def _suggest_python_improvements(self, code):
        """Saran perbaikan Python"""
        lines = code.split('\n')
        has_function = any('def ' in line for line in lines)
        has_class = any('class ' in line for line in lines)
        
        if has_function and not any('"""' in line or "'''" in line for line in lines):
            self.improvement_suggestions.append("📝 Tambahkan docstring untuk fungsi/class")
        if has_function and 'try:' not in code and 'except' not in code:
            self.improvement_suggestions.append("🛡️ Tambahkan error handling (try-except)")
        if has_function and '->' not in code:
            self.improvement_suggestions.append("🎯 Pertimbangkan menambahkan type hints")
    
    def _analyze_javascript(self, code):
        """Analisis kode JavaScript"""
        self._check_javascript_syntax(code)
        self._check_javascript_style(code)
        self._suggest_javascript_improvements(code)
        return self._format_results()
    
    def _check_javascript_syntax(self, code):
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            self.syntax_errors.append(f"❌ Kurung kurawal tidak seimbang: {{={open_braces}, }}={close_braces}")
        else:
            self.syntax_errors.append("✅ Tidak ditemukan error sintaks dasar")
    
    def _check_javascript_style(self, code):
        lines = code.split('\n')
        if 'var ' in code:
            self.style_issues.append("🎨 Gunakan let/const daripada var")
    
    def _suggest_javascript_improvements(self, code):
        if '==' in code or '!=' in code:
            self.improvement_suggestions.append("🎯 Gunakan === dan !== daripada == dan !=")
    
    def _analyze_cpp(self, code):
        self._check_cpp_syntax(code)
        self._check_cpp_style(code)
        self._suggest_cpp_improvements(code)
        return self._format_results()
    
    def _check_cpp_syntax(self, code):
        if code.count('{') != code.count('}'):
            self.syntax_errors.append("❌ Kurung kurawal tidak seimbang")
        else:
            self.syntax_errors.append("✅ Tidak ditemukan error sintaks dasar")
    
    def _check_cpp_style(self, code):
        if 'using namespace std;' in code:
            self.style_issues.append("🎨 Hindari 'using namespace std' di scope global")
    
    def _suggest_cpp_improvements(self, code):
        if 'malloc' in code or 'free' in code:
            self.improvement_suggestions.append("⚡ Gunakan new/delete daripada malloc/free")
    
    def _format_results(self):
        """Format hasil analisis"""
        if not any('❌' in e for e in self.syntax_errors):
            if not self.syntax_errors:
                self.syntax_errors = ['✅ Tidak ditemukan error sintaks']
            else:
                self.syntax_errors = [msg.replace('⚠️', '💡') for msg in self.syntax_errors]
        
        if not self.style_issues:
            self.style_issues = ['🎨 Gaya penulisan baik']
        if not self.efficiency_suggestions:
            self.efficiency_suggestions = ['⚡ Tidak ada saran efisiensi']
        if not self.improvement_suggestions:
            self.improvement_suggestions = ['💡 Tidak ada saran perbaikan tambahan']
        
        return {
            'syntax_errors': self.syntax_errors,
            'style_issues': self.style_issues,
            'efficiency_suggestions': self.efficiency_suggestions,
            'improvement_suggestions': self.improvement_suggestions
        }

    # === Integrasi AI Feedback (Groq) - OPSIONAL ===
    def get_ai_feedback(self, analysis_result):
        """
        Minta umpan balik tambahan dari AI Groq (opsional)
        """
        if not self.client:
            return "❌ AI features tidak tersedia (Groq tidak terinstall atau GROQ_API_KEY tidak diset)"
        
        system_prompt = """
        Kamu adalah asisten AI ahli dalam analisis kualitas kode.
        Tugasmu: berikan umpan balik profesional berdasarkan hasil analisis manual.
        """

        user_prompt = f"""
        Hasil analisis manual:
        {analysis_result}

        Beri umpan balik tambahan:
        1. Ringkasan kualitas kode (1 paragraf)
        2. Saran perbaikan utama (3 poin)
        3. (Opsional) Contoh potongan kode yang diperbaiki
        """

        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Model yang lebih umum
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=1000  # Fixed reasonable limit
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Gagal mengambil feedback AI: {e}"
