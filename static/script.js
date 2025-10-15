// helper escape
function escapeHtml(unsafe) {
    return (unsafe||"")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({behavior: 'smooth'});
}

function hideError() {
    const errorSection = document.getElementById('errorSection');
    errorSection.style.display = 'none';
}

function setLoadingState(isLoading) {
    const reviewBtn = document.getElementById('reviewBtn');
    const btnText = reviewBtn.querySelector('.btn-text');
    const btnLoading = reviewBtn.querySelector('.btn-loading');
    if (isLoading) {
        reviewBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        reviewBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

function displayResultList(elementId, items) {
    const element = document.getElementById(elementId);
    if (!Array.isArray(items)) {
        element.innerHTML = '<p>Tidak ada data</p>';
        return;
    }
    if (items.length === 0) {
        element.innerHTML = '<p>-</p>';
        return;
    }
    element.innerHTML = '<ul>' + items.map(i => `<li>${escapeHtml(i)}</li>`).join('') + '</ul>';
}

function displayResults(result) {
    if (!result) {
        showError('Hasil analisis tidak valid dari server.');
        return;
    }

    displayResultList('syntaxErrors', result.syntax_errors || []);
    displayResultList('styleIssues', result.style_issues || []);
    displayResultList('efficiencySuggestions', result.efficiency_suggestions || []);
    displayResultList('improvementSuggestions', result.improvement_suggestions || []);

    // AI fixed code
    const aiFixed = result.ai_fixed_code;
    const aiNote = result.ai_note;
    const aiFixedCodeEl = document.querySelector('#aiFixedCode code');
    const copyBtn = document.getElementById('copyBtn');
    const aiNoteEl = document.getElementById('aiNote');

    if (aiFixed && aiFixed.trim()) {
        aiFixedCodeEl.innerHTML = escapeHtml(aiFixed);
        copyBtn.style.display = 'inline-block';
    } else {
        aiFixedCodeEl.innerHTML = '<em>Tidak ada perbaikan otomatis dari AI.</em>';
        copyBtn.style.display = 'none';
    }
    aiNoteEl.textContent = aiNote || '';

    document.getElementById('resultSection').style.display = 'block';
    document.getElementById('resultSection').scrollIntoView({behavior: 'smooth'});
}

async function reviewCode() {
    const codeInput = document.getElementById('codeInput');
    const languageSelect = document.getElementById('language');

    const code = codeInput.value.trim();
    const language = languageSelect.value;

    if (!code) {
        showError('Silakan masukkan kode terlebih dahulu');
        return;
    }

    hideError();
    setLoadingState(true);

    try {
        const res = await fetch('/review', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code, language})
        });
        const data = await res.json();

        if (!data.success) {
            showError(data.error || 'Terjadi kesalahan saat menganalisis kode');
        } else {
            displayResults(data.result);
        }
    } catch (err) {
        showError('Terjadi kesalahan jaringan: ' + (err.message || err));
    } finally {
        setLoadingState(false);
    }
}

function copyFixedCode() {
    const code = document.querySelector('#aiFixedCode code').innerText;
    navigator.clipboard.writeText(code);
    alert('Kode hasil perbaikan disalin ke clipboard');
}

// optional: Ctrl/Cmd+Enter to run
document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('codeInput');
    codeInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            reviewCode();
        }
    });

    // load example
    const example = `# Contoh kode Python
def HitungLuas(panjang,lebar):
hasil=panjang*lebar
return hasil

print(HitungLuas(5, 2))`;
    codeInput.value = example;
});
