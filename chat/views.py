from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Message
from users.models import CustomUser

@login_required
def inbox_view(request):
    conversations_qs = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    conversations = []
    for conv in conversations_qs:
        conv.other_user = conv.get_other_participant(request.user)
        conversations.append(conv)

    selected_conv = None
    conversation_id = request.GET.get('conv')
    show_chat = False
    
    if conversation_id:
        selected_conv = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
        show_chat = True
    elif len(conversations) > 0 and not request.GET.get('list'):
        selected_conv = conversations[0]
        # On desktop, show selected_conv. On mobile, if explicitly requested, show list.

    messages_list = []
    other_user = None
    if selected_conv:
        other_user = selected_conv.get_other_participant(request.user)
        messages_list = selected_conv.messages.select_related('sender').order_by('created_at')
        # Mark as read
        selected_conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    context = {
        'conversations': conversations,
        'selected_conv': selected_conv,
        'other_user': other_user,
        'messages_list': messages_list,
        'show_chat': show_chat,
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def start_conversation_view(request, username):
    target_user = get_object_or_404(CustomUser, username=username)

    if target_user == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('dashboard:dashboard')

    # Find existing conversation
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=target_user)
    
    if conversations.exists():
        conv = conversations.first()
    else:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, target_user)

    return redirect(f"/chat/?conv={conv.pk}")


@login_required
def send_message_api(request, conv_id):
    if request.method == 'POST':
        conv = get_object_or_404(Conversation, pk=conv_id, participants=request.user)
        text = request.POST.get('message', '').strip()

        if text:
            msg = Message.objects.create(
                conversation=conv,
                sender=request.user,
                text=text
            )
            conv.save() # update timestamp
            return JsonResponse({
                'status': 'ok',
                'id': msg.id,
                'message': msg.text,
                'sender': msg.sender.username,
                'created_at': msg.created_at.strftime('%H:%M'),
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def fetch_messages_api(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id, participants=request.user)
    last_id = request.GET.get('after_id', 0)
    try:
        last_id = int(last_id)
    except ValueError:
        last_id = 0

    new_messages = conv.messages.filter(id__gt=last_id).select_related('sender').order_by('created_at')
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = []
    for msg in new_messages:
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.text,
            'created_at': msg.created_at.strftime('%H:%M')
        })

    return JsonResponse({'messages': data})
