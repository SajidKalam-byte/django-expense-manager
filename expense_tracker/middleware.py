from django.shortcuts import redirect

class GlobalLoginRequiredMiddleware:
    """
    Forces every single page in the Django app to require a login.
    If the user is not logged in, they are immediately redirected to the admin login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Allow access to the admin login page so they don't get stuck in an infinite redirect loop
            if not request.path.startswith('/admin/'):
                return redirect(f"/admin/login/?next={request.path}")
        return self.get_response(request)
