"""
Revenue Service
Centralises commission/revenue split logic to avoid DRY violations.
"""

def calculate_revenue_split(booking):
    """
    Calculate the owner and worker revenue split for a completed booking.

    Returns a dict: {'worker_amt': float, 'owner_amt': float}
    """
    if not booking.service:
        return {'worker_amt': 0.0, 'owner_amt': 0.0}

    total_price = float(booking.service.price)
    worker_amt = 0.0

    if booking.worker:
        if booking.worker.is_owner:
            # Owner-worker: 100% goes to owner
            worker_amt = 0.0
        elif booking.worker.payment_type == 'salary':
            # Salaried worker: no commission
            worker_amt = 0.0
        else:
            # Commission-based worker
            rate = booking.worker.commission_rate or 50.0
            worker_amt = (rate / 100.0) * total_price

    owner_amt = total_price - worker_amt
    return {'worker_amt': worker_amt, 'owner_amt': owner_amt}
