from django.contrib.auth.models import User
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAB(OIDCAuthenticationBackend):
    def provider_logout(request):
        redirect_url = 'https://secure-sso-opensubmit.192.168.99.100.nip.io/auth/realms/master/protocol/openid-connect/logout'
        return redirect_url

    def create_user(self, claims):
        username = claims.get('preferred_username', '')
        name = claims.get('name', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = self.UserModel.objects.create_user(username)
            user.first_name = name
            user.save()

        return user

    def update_user(self, user, claims):
        user.username = claims.get('preferred_username', '')
        user.first_name = claims.get('name', '')
        user.save()

        return user
