/**
 * Apex College Voting Portal - Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Ballot Candidate Card Selection
    const candidateRadios = document.querySelectorAll('.candidate-select-radio');
    const candidateCards = document.querySelectorAll('.candidate-card-selectable');

    candidateCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger twice if clicking radio directly
            const radio = this.querySelector('.candidate-select-radio');
            if (radio) {
                radio.checked = true;
                updateCandidateSelection();
            }
        });
    });

    candidateRadios.forEach(radio => {
        radio.addEventListener('change', updateCandidateSelection);
    });

    function updateCandidateSelection() {
        candidateCards.forEach(card => {
            const radio = card.querySelector('.candidate-select-radio');
            if (radio && radio.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
        
        // Enable submit button
        const submitBtn = document.getElementById('ballot-continue-btn');
        if (submitBtn) {
            submitBtn.removeAttribute('disabled');
        }
    }

    // 2. Copy Receipt Code to Clipboard
    const copyReceiptBtn = document.getElementById('copy-receipt-btn');
    if (copyReceiptBtn) {
        copyReceiptBtn.addEventListener('click', function() {
            const codeEl = document.getElementById('receipt-code');
            if (codeEl) {
                navigator.clipboard.writeText(codeEl.innerText.trim()).then(() => {
                    const originalText = copyReceiptBtn.innerHTML;
                    copyReceiptBtn.innerHTML = '<i class="bi bi-check-lg me-1"></i> Copied!';
                    copyReceiptBtn.classList.replace('btn-outline-primary', 'btn-success');
                    setTimeout(() => {
                        copyReceiptBtn.innerHTML = originalText;
                        copyReceiptBtn.classList.replace('btn-success', 'btn-outline-primary');
                    }, 2500);
                });
            }
        });
    }

    // 3. Confirm Dangerous Actions (Delete, Reject)
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const msg = this.getAttribute('data-confirm') || "Are you sure you want to proceed with this action?";
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // 4. Initialize Bootstrap Tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(el) {
            return new bootstrap.Tooltip(el);
        });
    }
});
