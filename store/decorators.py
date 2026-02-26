# store/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def admin_only(view_func):
    """
    Decorator: only allows users with Profile.role == 'admin'
    """
    def check_admin(user):
        if not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)  # safe access
        return profile and profile.role == 'admin'

    decorated = user_passes_test(
        check_admin,
        login_url='login',          # or your login url name
        redirect_field_name='next'
    )
    return decorated(view_func)


def staff_or_admin_only(view_func):
    """
    Decorator: allows 'staff' or 'admin'
    """
    def check_staff_or_admin(user):
        if not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)
        return profile and profile.role in ('staff', 'admin')

    decorated = user_passes_test(
        check_staff_or_admin,
        login_url='login',
        redirect_field_name='next'
    )
    return decorated(view_func)