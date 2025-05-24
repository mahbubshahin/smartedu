from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsername(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        # চেষ্টা করুন ইমেইল বা ইউজারনেম দিয়ে লগইন করার
        try:
            user = User.objects.get(
                **{User.USERNAME_FIELD: username} if '@' in username else {'username': username}
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
