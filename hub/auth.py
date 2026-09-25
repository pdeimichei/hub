"""Authentication helpers for local development and Azure App Service Easy Auth."""

from functools import wraps

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden

ENTRA_PRINCIPAL_HEADER = "HTTP_X_MS_CLIENT_PRINCIPAL_NAME"


def entra_principal(request):
    """Return the UPN/email injected by Azure App Service Easy Auth."""
    return request.META.get(ENTRA_PRINCIPAL_HEADER, "").strip()


def current_username(request):
    """Return the Azure Entra principal, or the local Django user in development."""
    principal = entra_principal(request)
    if principal:
        return principal

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return user.get_username()

    return ""


def app_login_required(view_func):
    """
    Azure: trust only the identity header injected by App Service Easy Auth.
    Local development: fall back to Django authentication.
    """

    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if entra_principal(request):
            return view_func(request, *args, **kwargs)

        if settings.AZURE_ENTRA_AUTH:
            return HttpResponseForbidden("Microsoft Entra authentication required.")

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return view_func(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

    return wrapped
