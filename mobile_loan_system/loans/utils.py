"""
Pure-logic helpers for EMI (Equated Monthly Installment) calculations.
Kept separate from models.py so the math can be unit-tested in isolation.
"""
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta


def calculate_emi(principal: Decimal, annual_interest_rate: Decimal, tenure_months: int) -> Decimal:
    """
    Standard reducing-balance EMI formula:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    where r = monthly interest rate (annual_rate / 12 / 100).

    If the interest rate is 0, it's a simple equal split of the principal.
    """
    principal = Decimal(principal)
    tenure_months = int(tenure_months)

    if annual_interest_rate == 0:
        emi = principal / tenure_months
    else:
        r = Decimal(annual_interest_rate) / Decimal(12) / Decimal(100)
        factor = (1 + r) ** tenure_months
        emi = principal * r * factor / (factor - 1)

    return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def build_schedule(principal: Decimal, annual_interest_rate: Decimal, tenure_months: int, start_date):
    """
    Returns a list of dicts describing each installment:
        [{'installment_number': 1, 'due_date': date, 'amount_due': Decimal}, ...]
    The last installment absorbs any rounding difference so the total
    exactly equals principal (+ interest, if any).
    """
    emi = calculate_emi(principal, annual_interest_rate, tenure_months)
    schedule = []

    for i in range(1, tenure_months + 1):
        due_date = start_date + relativedelta(months=i)
        schedule.append({
            'installment_number': i,
            'due_date': due_date,
            'amount_due': emi,
        })
    return schedule
