from django.shortcuts import render, HttpResponse
from apps.system_setting.models import SystemColor
from apps.user.models import User
from django.utils import timezone
from datetime import datetime
# Create your views here.

def dashboard_callback(request, context):
    now = timezone.now()

    start_of_month = now.replace(day=1)
    total_subscribers = 20
    total_new_subscriptions = 5
    total_income = 1000

    if now.month == 12:
        start_of_next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        start_of_next_month = now.replace(month=now.month + 1, day=1)

    system_color = SystemColor.objects.filter(is_active=True).first().code

    context.update(
        {
            "system_color": system_color,
            "total_users": User.objects.count(),
            "total_subscriptions": total_subscribers,
            "total_income": total_income,
            "total_new_subscriptions": total_new_subscriptions,
            "current_month_signups": User.objects.filter(
                created_at__gte=start_of_month,
                created_at__lt=start_of_next_month
            ).count(),
            "admins": User.objects.filter(is_staff=True).count(),
            "supper_admins": User.objects.filter(is_superuser=True).count(),
            "data": [
                User.objects.filter(
                    created_at__year=datetime.now().year,
                    created_at__month=m
                ).count() for m in range(1, 13)
            ]
        }
    )

    return context
