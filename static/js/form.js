// ── Form UX Enhancements ──────────────────────────────────────────────────────

// Income: format as user types
const incomeInput = document.querySelector('input[name="annual_income"]');
if (incomeInput) {
  incomeInput.addEventListener('input', function () {
    const val = parseInt(this.value.replace(/\D/g, ''), 10);
    if (!isNaN(val)) {
      // Show hint about category
      const hint = this.parentElement.querySelector('.form-hint');
      if (hint) {
        if (val <= 50000)       hint.textContent = '💚 Likely eligible for BPL schemes — check BPL card option';
        else if (val <= 100000) hint.textContent = '💚 Eligible for most welfare schemes';
        else if (val <= 200000) hint.textContent = '🟡 Eligible for many central government schemes';
        else if (val <= 300000) hint.textContent = '🟡 Eligible for select schemes (PMAY, MUDRA etc.)';
        else                    hint.textContent = '🔵 You may qualify for loan/credit schemes';
      }
    }
  });
}

// Auto-suggest BPL if income very low
const bplSelect = document.querySelector('select[name="bpl_card"]');
if (incomeInput && bplSelect) {
  incomeInput.addEventListener('change', function () {
    const val = parseInt(this.value, 10);
    if (val <= 60000 && bplSelect.value === 'no') {
      bplSelect.parentElement.style.border = '2px solid var(--gold)';
      bplSelect.parentElement.querySelector('.form-hint').textContent =
        '⚠️ With this income, you may be eligible for a BPL card — check with your local office';
    }
  });
}

// Form submission animation
const form = document.getElementById('eligibility-form');
if (form) {
  form.addEventListener('submit', function (e) {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ Finding your schemes...';
      btn.style.opacity = '0.8';
    }
  });
}
