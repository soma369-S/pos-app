// Live EMI preview calculator used on the loan-application page.
// Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1), where r = monthly interest rate.
function calculateEMI(principal, downPayment, annualRate, months) {
    const loanAmount = principal - downPayment;
    if (loanAmount <= 0 || months <= 0) return 0;
    const monthlyRate = (annualRate / 100) / 12;
    if (monthlyRate === 0) return loanAmount / months;
    const factor = Math.pow(1 + monthlyRate, months);
    return (loanAmount * monthlyRate * factor) / (factor - 1);
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loan-form');
    if (!form) return;

    const principal = parseFloat(form.dataset.principal || '0');
    const downPaymentInput = form.querySelector('[name="down_payment"]');
    const interestInput = form.querySelector('[name="interest_rate"]');
    const tenureInput = form.querySelector('[name="tenure_months"]');
    const emiOutput = document.getElementById('emi-preview');

    function update() {
        const dp = parseFloat(downPaymentInput.value || '0');
        const rate = parseFloat(interestInput.value || '0');
        const months = parseInt(tenureInput.value || '0', 10);
        const emi = calculateEMI(principal, dp, rate, months);
        emiOutput.textContent = '₹' + emi.toFixed(2);
    }

    [downPaymentInput, interestInput, tenureInput].forEach(el => {
        el.addEventListener('input', update);
        el.addEventListener('change', update);
    });
    update();
});
