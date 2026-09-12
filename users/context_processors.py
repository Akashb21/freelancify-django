def unread_notifications(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(is_read=False)[:5]
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {
            'header_notifications': notifications,
            'unread_notifications_count': unread_count,
        }
    return {
        'header_notifications': [],
        'unread_notifications_count': 0,
    }
