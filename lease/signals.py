"""
Django signals for the lease app.

First signals.py in units-backend (see lease/apps.py's LeaseConfig.ready()).
Registers the sole trigger mechanism for notifying Finance (units-finance)
of LeaseTransaction creates/status changes -- AD-4 in
docs/finance/ARCHITECTURE-SPINE.md. No polling, no Celery, no Redis, no
queue: this synchronous post_save receiver is the only event source.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from lease.finance_sync import sync_lease_transaction_to_finance
from lease.models import LeaseTransaction


@receiver(post_save, sender=LeaseTransaction)
def sync_lease_transaction_on_save(sender, instance, created, **kwargs):
    """
    Fires on every LeaseTransaction.save() (create and update) -- no
    filtering on which fields changed. Finance's own idempotency check
    (Story 2.2+) is what prevents duplicate postings, not this signal.
    """
    sync_lease_transaction_to_finance(instance.id)
