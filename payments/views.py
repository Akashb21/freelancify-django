from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import Transaction
from contracts.models import Contract
from users.models import Notification
from .utils import generate_invoice_pdf
import uuid

@login_required
def checkout_view(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, client=request.user)

    if contract.is_escrow_funded:
        messages.info(request, "Escrow is already funded for this contract.")
        return redirect('contracts:contract_detail', pk=contract.pk)

    context = {
        'contract': contract,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def process_checkout(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, client=request.user)

    if request.method == 'POST':
        # Create transaction record
        tx = Transaction.objects.create(
            contract=contract,
            payer=contract.client,
            payee=contract.freelancer,
            amount=contract.agreed_amount,
            status='ESCROW_HELD',
            stripe_payment_id=f"pi_mock_{uuid.uuid4().hex[:12]}",
            description=f"Escrow deposit for contract #{contract.id} ({contract.job.title})"
        )

        contract.is_escrow_funded = True
        contract.save()

        # Notify Freelancer
        Notification.objects.create(
            user=contract.freelancer,
            title="Escrow Funded! 🔒",
            message=f"{contract.client.username} deposited ${contract.agreed_amount} into escrow for contract '{contract.job.title}'. You can now begin work!",
            link=f"/contracts/{contract.pk}/"
        )

        messages.success(request, f"Payment of ${contract.agreed_amount} successfully deposited into Escrow!")
        return redirect('contracts:contract_detail', pk=contract.pk)

    return redirect('payments:checkout', contract_id=contract.id)


@login_required
def download_invoice(request, transaction_id):
    tx = get_object_or_404(Transaction, pk=transaction_id)

    if request.user != tx.payer and request.user != tx.payee and not request.user.is_superuser:
        messages.error(request, "You are not authorized to download this invoice.")
        return redirect('dashboard:dashboard')

    pdf_buffer = generate_invoice_pdf(tx)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{str(tx.invoice_number)[:8].upper()}.pdf"'
    return response


@login_required
def transaction_history(request):
    if request.user.is_client():
        transactions = Transaction.objects.filter(payer=request.user).select_related('contract', 'payee')
    else:
        transactions = Transaction.objects.filter(payee=request.user).select_related('contract', 'payer')

    return render(request, 'payments/transaction_history.html', {'transactions': transactions})
