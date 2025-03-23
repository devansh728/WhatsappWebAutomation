from django.shortcuts import render, get_object_or_404
import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage, MediaFile

def index(request):
    """Home page view that displays a dashboard-style overview."""
    # Count statistics
    total_messages = ChatMessage.objects.count()
    total_senders = ChatMessage.objects.values('sender').distinct().count()
    total_media = MediaFile.objects.count()
    
    # Recent chats (top 5 most recent)
    recent_chats = ChatMessage.objects.values('sender', 'receiver').distinct()[:5]
    
    # Context data for the template
    context = {
        'total_messages': total_messages,
        'total_senders': total_senders,
        'total_media': total_media,
        'recent_chats': recent_chats,
    }
    
    return render(request, 'whatsapp/index.html', context)

@login_required
def message_list(request):
    """View for displaying all messages with filtering and pagination."""
    # Get filter parameters from request
    sender = request.GET.get('sender', '')
    receiver = request.GET.get('receiver', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('q', '')
    
    # Start with all messages
    messages = ChatMessage.objects.all().order_by('-timestamp')
    
    # Apply filters if provided
    if sender:
        messages = messages.filter(sender=sender)
    if receiver:
        messages = messages.filter(receiver=receiver)
    if date_from:
        messages = messages.filter(date__gte=date_from)
    if date_to:
        messages = messages.filter(date__lte=date_to)
    if search_query:
        messages = messages.filter(
            Q(message__icontains=search_query) | 
            Q(sender__icontains=search_query) | 
            Q(receiver__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(messages, 25)  # 25 messages per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique senders and receivers for filter dropdowns
    senders = ChatMessage.objects.values_list('sender', flat=True).distinct()
    receivers = ChatMessage.objects.values_list('receiver', flat=True).distinct()
    
    # Context data for the template
    context = {
        'page_obj': page_obj,
        'senders': senders,
        'receivers': receivers,
        'filters': {
            'sender': sender,
            'receiver': receiver,
            'date_from': date_from,
            'date_to': date_to,
            'q': search_query,
        }
    }
    
    return render(request, 'whatsapp/message_list.html', context)

@login_required
def message_detail(request, message_id):
    """View for displaying the details of a specific message."""
    message = get_object_or_404(ChatMessage, pk=message_id)
    
    # Parse media URLs if they exist
    media_data = []
    if message.media_urls:
        try:
            media_data = json.loads(message.media_urls)
        except json.JSONDecodeError:
            pass
    
    # Get associated media files
    media_files = MediaFile.objects.filter(chat_message=message)
    
    context = {
        'message': message,
        'media_data': media_data,
        'media_files': media_files,
    }
    
    return render(request, 'whatsapp/message_detail.html', context)

@login_required
def media_list(request):
    """View for displaying all media files with filtering and pagination."""
    # Get filter parameters from request
    media_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    downloaded = request.GET.get('downloaded', '')
    
    # Start with all media files
    media_files = MediaFile.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    if media_type:
        media_files = media_files.filter(file_type=media_type)
    if date_from:
        media_files = media_files.filter(created_at__date__gte=date_from)
    if date_to:
        media_files = media_files.filter(created_at__date__lte=date_to)
    if downloaded == 'yes':
        media_files = media_files.filter(downloaded=True)
    elif downloaded == 'no':
        media_files = media_files.filter(downloaded=False)
    
    # Pagination
    paginator = Paginator(media_files, 20)  # 20 media files per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'media_types': MediaFile.MEDIA_TYPES,
        'filters': {
            'type': media_type,
            'date_from': date_from,
            'date_to': date_to,
            'downloaded': downloaded,
        }
    }
    
    return render(request, 'whatsapp/media_list.html', context)

@csrf_exempt
def api_messages(request):
    """API endpoint for fetching messages in JSON format."""
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    sender = request.GET.get('sender', '')
    
    messages = ChatMessage.objects.all().order_by('-timestamp')
    
    if sender:
        messages = messages.filter(sender=sender)
    
    messages = messages[offset:offset+limit]
    
    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'sender': msg.sender,
            'receiver': msg.receiver,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
            'date': msg.date.isoformat(),
            'has_media': bool(msg.media_urls),
        })
    
    return JsonResponse({'messages': result, 'count': len(result)})

@csrf_exempt
def api_chat_summary(request):
    """API endpoint for getting chat statistics."""
    # Get overall statistics
    total_messages = ChatMessage.objects.count()
    total_senders = ChatMessage.objects.values('sender').distinct().count()
    total_receivers = ChatMessage.objects.values('receiver').distinct().count()
    total_media = MediaFile.objects.count()
    
    # Get top 5 most active chats (by message count)
    top_chats = []
    chat_stats = {}
    
    # Group by sender-receiver pair
    messages = ChatMessage.objects.all()
    for msg in messages:
        chat_key = f"{msg.sender}|{msg.receiver}"
        if chat_key in chat_stats:
            chat_stats[chat_key] += 1
        else:
            chat_stats[chat_key] = 1
    
    # Sort and take top 5
    sorted_chats = sorted(chat_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    for chat, count in sorted_chats:
        sender, receiver = chat.split('|')
        top_chats.append({
            'sender': sender,
            'receiver': receiver,
            'count': count
        })
    
    response_data = {
        'stats': {
            'total_messages': total_messages,
            'total_senders': total_senders,
            'total_receivers': total_receivers,
            'total_media': total_media,
        },
        'top_chats': top_chats
    }
    
    return JsonResponse(response_data)
