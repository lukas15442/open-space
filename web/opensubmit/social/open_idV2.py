from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAB(OIDCAuthenticationBackend):
    def provider_logout(request):
        redirect_url = 'https://secure-sso-opensubmit.192.168.99.100.nip.io/auth/realms/master/protocol/openid-connect/logout'
        return redirect_url
