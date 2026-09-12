from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Contract, WorkSubmission, Review
from users.models import Notification

@login_required
def contract_list_view(request):
    if request.user.is_client():
        contracts = Contract.objects.filter(client=request.user).select_related('freelancer', 'job')
    else:
        contracts = Contract.objects.filter(freelancer=request.user).select_related('client', 'job')

    return render(request, 'contracts/contract_list.html', {'contracts': contracts})


@login_required
def contract_detail_view(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.user != contract.client and request.user != contract.freelancer and not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this contract.")
        return redirect('dashboard:dashboard')

    submissions = contract.submissions.all()
    user_review = contract.reviews.filter(reviewer=request.user).first()
    other_review = contract.reviews.exclude(reviewer=request.user).first()

    context = {
        'contract': contract,
        'submissions': submissions,
        'user_review': user_review,
        'other_review': other_review,
    }
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def submit_work_view(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.user != contract.freelancer:
        messages.error(request, "Only the assigned freelancer can submit work for this contract.")
        return redirect('contracts:contract_detail', pk=contract.pk)

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        external_url = request.POST.get('external_url', '')
        file_attachment = request.FILES.get('file_attachment', None)

        WorkSubmission.objects.create(
            contract=contract,
            message=message_text,
            external_url=external_url,
            file_attachment=file_attachment
        )

        contract.status = 'SUBMITTED'
        contract.save()

        # Notify Client
        Notification.objects.create(
            user=contract.client,
            title=f"Work Submitted for '{contract.job.title[:30]}...'",
            message=f"{request.user.username} has submitted work for your review.",
            link=f"/contracts/{contract.pk}/"
        )

        messages.success(request, "Your work submission has been delivered to the client!")
        return redirect('contracts:contract_detail', pk=contract.pk)

    return render(request, 'contracts/submit_work.html', {'contract': contract})


@login_required
def approve_work_view(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.user != contract.client:
        messages.error(request, "Only the client can approve submitted work.")
        return redirect('contracts:contract_detail', pk=contract.pk)

    contract.status = 'COMPLETED'
    contract.completed_at = timezone.now()
    contract.save()

    # Update job status
    contract.job.status = 'COMPLETED'
    contract.job.save()

    # Release funds to freelancer profile balance
    freelancer_profile = contract.freelancer.profile
    freelancer_profile.total_earnings += contract.agreed_amount
    freelancer_profile.save()

    client_profile = contract.client.profile
    client_profile.total_spent += contract.agreed_amount
    client_profile.save()

    # Create transaction record
    from payments.models import Transaction
    Transaction.objects.create(
        contract=contract,
        payer=contract.client,
        payee=contract.freelancer,
        amount=contract.agreed_amount,
        status='RELEASED',
        description=f"Escrow released for completed contract #{contract.id}"
    )

    # Notify Freelancer
    Notification.objects.create(
        user=contract.freelancer,
        title=f"Work Approved & Payment Released! 💰",
        message=f"{contract.client.username} approved your work and released ${contract.agreed_amount}.",
        link=f"/contracts/{contract.pk}/"
    )

    messages.success(request, f"Work approved! ${contract.agreed_amount} has been released to {contract.freelancer.username}.")
    return redirect('contracts:contract_detail', pk=contract.pk)


@login_required
def add_review_view(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.user != contract.client and request.user != contract.freelancer:
        messages.error(request, "Unauthorized to leave review.")
        return redirect('contracts:contract_detail', pk=contract.pk)

    reviewee = contract.freelancer if request.user == contract.client else contract.client

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        feedback = request.POST.get('feedback', '')

        Review.objects.create(
            contract=contract,
            reviewer=request.user,
            reviewee=reviewee,
            rating=rating,
            feedback=feedback
        )

        # Update average rating of reviewee
        reviews = Review.objects.filter(reviewee=reviewee)
        avg = sum([r.rating for r in reviews]) / len(reviews)
        profile = reviewee.profile
        profile.rating_average = avg
        profile.rating_count = len(reviews)
        profile.save()

        messages.success(request, f"Thank you! Your {rating}-star review for {reviewee.username} has been published.")
        return redirect('contracts:contract_detail', pk=contract.pk)

    return render(request, 'contracts/add_review.html', {'contract': contract, 'reviewee': reviewee})
