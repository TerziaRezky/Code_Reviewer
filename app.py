from flask import Flask, render_template, request, jsonify
import os
import sys

# Pastikan current dir ada di sys.path supaya import package lokal berhasil
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import analyzer lokal (rule-based) & AI feedback module
try:
    from ai_engine.analyzer import CodeAnalyzer
    print("✅ Berhasil import CodeAnalyzer")
except Exception as e:
    print(f"❌ Gagal import CodeAnalyzer: {e}")
    # Minimal fallback (tidak ideal, hanya untuk mencegah crash)
    class CodeAnalyzer:
        def analyze_code(self, code, language='python'):
            return {
                "syntax_errors": ["Analisis lokal tidak tersedia (fallback)"],
                "style_issues": [],
                "efficiency_suggestions": [],
                "improvement_suggestions": []
            }

try:
    from ai_engine.ai_feedback import AIFeedback
    print("✅ Berhasil import AIFeedback")
except Exception as e:
    print(f"⚠️ AIFeedback tidak tersedia: {e}")
    AIFeedback = None  # handler nanti

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/review', methods=['POST'])
def review_code():
    """
    Expects JSON:
    { "code": "...", "language": "python" }
    Returns:
    {
      "success": True,
      "result": {
          "syntax_errors": [...],
          "style_issues": [...],
          "efficiency_suggestions": [...],
          "improvement_suggestions": [...],
          "ai_fixed_code": "<fixed code or empty if none>",
          "ai_note": "<optional message>"
      }
    }
    """
    try:
        data = request.get_json(force=True)
        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code or not code.strip():
            return jsonify({"success": False, "error": "Kode tidak boleh kosong"}), 400

        analyzer = CodeAnalyzer()
        local_result = analyzer.analyze_code(code, language)

        # Ensure local_result has required keys
        for k in ['syntax_errors', 'style_issues', 'efficiency_suggestions', 'improvement_suggestions']:
            if k not in local_result:
                local_result[k] = []

        # Default AI outputs
        ai_fixed_code = None
        ai_note = None

        # If AIFeedback available, try to get fixed code
        if AIFeedback is not None:
            try:
                ai = AIFeedback()
                ai_fixed_code = ai.request_fixed_code(code, language)
                ai_note = None
            except Exception as e:
                ai_fixed_code = None
                ai_note = f"AI unavailable or failed: {str(e)}"

        result = {
            "syntax_errors": local_result.get("syntax_errors", []),
            "style_issues": local_result.get("style_issues", []),
            "efficiency_suggestions": local_result.get("efficiency_suggestions", []),
            "improvement_suggestions": local_result.get("improvement_suggestions", []),
            "ai_fixed_code": ai_fixed_code,
            "ai_note": ai_note
        }

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": f"Terjadi kesalahan: {str(e)}"}), 500


if __name__ == '__main__':
    # Jalankan secara lokal
    print("🚀 Menjalankan AI Code Reviewer Flask App (Local)...")
    print(f"📁 Current dir: {current_dir}")
    
    ai_engine_path = os.path.join(current_dir, 'ai_engine')
    if os.path.exists(ai_engine_path):
        print(f"📂 ai_engine files: {os.listdir(ai_engine_path)}")

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
