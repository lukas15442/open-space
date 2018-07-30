from django.contrib.auth.models import User
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from opensubmit import settings


class MyOIDCAB(OIDCAuthenticationBackend):
    def provider_logout(request):
        redirect_url = settings.OIDC_OP_LOGOUT_URL_METHOD
        return redirect_url

    def create_user(self, claims):
        username = claims.get('preferred_username', '')
        name = claims.get('name', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = self.UserModel.objects.create_user(username)
            user.first_name = name
            user.profile.student_id = username
            user.profile.save()
            user.save()

        return user

    def update_user(self, user, claims):
        user.username = claims.get('preferred_username', '')
        user.first_name = claims.get('name', '')
        user.profile.student_id = user.username
        user.profile.save()
        user.save()

        return user
