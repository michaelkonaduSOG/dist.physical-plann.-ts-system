from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User

def login_view(request):
    if request.method == 'POST':
        collector_id = request.POST.get('collector_id')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(collector_id=collector_id)
        except User.DoesNotExist:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid ID or password'
            })

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        # ✅ authentication check
        if user is not None and user.is_active:

            # 🔒 ROLE LOCK (IMPORTANT PART)
            if user.role != "COLLECTOR":
                return render(request, 'accounts/login.html', {
                    'error': 'This account is not allowed to access collector login'
                })

            login(request, user)
            return redirect('dashboard')

        return render(request, 'accounts/login.html', {
            'error': 'Invalid ID or password'
        })

    return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')