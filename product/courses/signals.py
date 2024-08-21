from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_list_or_404

from courses.models import Group
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.
    """
    if created:
        group = get_group_with_min_users(instance.course)
        group.users.add(instance.user)


def get_group_with_min_users(course):
    """
    Получить группу с наименьшим количеством пользователей.
    """
    groups = Group.objects.filter(course=course).annotate(users_count=Count('users')).order_by('users_count')
    return get_list_or_404(groups)[0]
