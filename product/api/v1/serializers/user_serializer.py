from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from djoser.serializers import UserSerializer
from rest_framework import serializers

from courses.models import Group
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    user = serializers.ReadOnlyField(source='user.id')
    course = serializers.ReadOnlyField(source='course.id')

    class Meta:
        model = Subscription
        fields = ('user', 'course')

    def validate(self, attrs):
        request = self.context.get('request')
        course = self.context.get('course')
        user = request.user

        self.check_course_purchased(user, course)
        self.check_user_balance(user, course)
        self.check_available_groups(course)

        return attrs

    def check_course_purchased(self, user, course):
        """Проверка, был ли приобретен курс ранее."""
        if course in user.courses.all():
            raise serializers.ValidationError(
                f'Пользователь {user.username} уже приобрел курс «{course.title}».'
            )

    def check_user_balance(self, user, course):
        """Проверка бонус для покупки курса."""
        if course.price > user.balance.bonuses_amount:
            raise serializers.ValidationError(
                f'У пользователя {user.username} недостаточно средств на '
                'покупку курса.'
            )

    def check_available_groups(self, course):
        """Проверка свободных мест в группах."""
        if not Group.objects.filter(course=course).annotate(
                users_num=Count('users')).filter(
                users_num__lt=settings.MAX_USERS_IN_GROUP).exists():
            raise serializers.ValidationError(
                f'Все группы на курс «{course.title}» заполнены.'
            )
