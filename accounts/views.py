from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    PasswordChangeView as BasePasswordChangeView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
from django.utils import timezone

from .forms import (
    LoginForm,
    PasswordResetRequestForm,
    ProfileUpdateForm,
    UserCreationForm,
    UserUpdateForm,
)
from .models import User, UserProfile, UserActivity


def is_staff_required(user):
    return user.is_active and (user.has_admin_role or user.is_staff)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_staff_required(self.request.user)


def record_activity(user, action, request=None, details=None):
    try:
        UserActivity.objects.create(
            user=user,
            action=action,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else '',
            details=details or {},
        )
    except Exception:
        pass


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        if user:
            login(self.request, user)
            user.last_login = timezone.now()
            user.last_login_ip = self.request.META.get('REMOTE_ADDR')
            user.save(update_fields=['last_login', 'last_login_ip'])
            record_activity(user, 'login', self.request, {'source': 'web'})
            messages.success(self.request, f'Welcome back, {user.get_full_name() or user.email}!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.request.user.has_admin_role:
            return reverse_lazy('dashboard:index')
        return reverse_lazy('accounts:profile')


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            record_activity(request.user, 'logout', request)
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        record_activity(user, 'register', self.request)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)
        return kwargs


class PasswordResetView(BasePasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetRequestForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(TemplateView):
    template_name = 'accounts/password_reset_complete.html'


class PasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        record_activity(self.request.user, 'password_change', self.request)
        messages.success(self.request, 'Your password has been updated successfully.')
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['profile'], _ = UserProfile.objects.get_or_create(user=user)
        context['activities'] = user.activities.all()[:20]
        context['recent_logins'] = user.activities.filter(action='login')[:10]
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_update.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        record_activity(self.request.user, 'profile_update', self.request)
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response


class UserListView(StaffRequiredMixin, ListView):
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        queryset = User.objects.select_related('role', 'branch', 'organization')
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search)
                | models.Q(username__icontains=search)
                | models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
                | models.Q(phone__icontains=search)
            )
        return queryset


class UserCreateView(StaffRequiredMixin, CreateView):
    template_name = 'accounts/user_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        UserProfile.objects.get_or_create(user=user)
        record_activity(self.request.user, 'user_create', self.request, {'target_user': str(user.id)})
        messages.success(self.request, f'User {user.email} created successfully.')
        return response


class UserUpdateView(StaffRequiredMixin, UpdateView):
    template_name = 'accounts/user_form.html'
    form_class = UserUpdateForm
    queryset = User.objects.select_related('role', 'branch', 'organization')
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        record_activity(self.request.user, 'user_update', self.request, {'target_user': str(self.object.id)})
        messages.success(self.request, f'User {self.object.email} updated successfully.')
        return response


class UserDeleteView(StaffRequiredMixin, DeleteView):
    template_name = 'accounts/user_confirm_delete.html'
    model = User
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        user = self.object
        if user == self.request.user:
            messages.error(self.request, 'You cannot delete your own account.')
            return redirect('accounts:user_list')
        record_activity(self.request.user, 'user_delete', self.request, {'target_user': str(user.id)})
        messages.success(self.request, f'User {user.email} deleted successfully.')
        return super().form_valid(form)


# Public Tracking Views
class PublicTrackingView(TemplateView):
    """Public cargo tracking page"""
    template_name = 'auth/track_cargo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Track public cargo access
        try:
            UserActivity.objects.create(
                user=None,
                action='cargo_tracking_access',
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:1000],
            )
        except Exception:
            pass
        return context


class EnhancedLoginView(BaseLoginView):
    """Enhanced login view with custom template"""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests - just display the login form"""
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests - authenticate user"""
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            from django.contrib import messages
            messages.error(request, 'Please provide both username/email and password.')
            return self.get(request, *args, **kwargs)
        
        # Try to authenticate with email or username
        from django.contrib.auth import authenticate
        from accounts.models import User

        # The User model uses EMAIL as USERNAME_FIELD, so authenticate() looks
        # up accounts by email. Support both email and username as the identifier.
        user = User.objects.filter(email__iexact=username).first()
        if user is None:
            user = User.objects.filter(username=username).first()

        if user is not None:
            auth_user = authenticate(request, username=user.email, password=password)
        else:
            auth_user = authenticate(request, username=username, password=password)
        
        if auth_user is not None and auth_user.is_active:
            login(request, auth_user)
            auth_user.last_login = timezone.now()
            auth_user.last_login_ip = request.META.get('REMOTE_ADDR')
            auth_user.save(update_fields=['last_login', 'last_login_ip'])
            
            record_activity(auth_user, 'login', request, {
                'source': 'web',
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
            })
            
            from django.contrib import messages
            messages.success(request, f'Welcome back!')
            return redirect(self.get_success_url())
        else:
            from django.contrib import messages
            messages.error(request, 'Invalid username/email or password.')
            return self.get(request, *args, **kwargs)
    
    def get_success_url(self):
        """Determine where to redirect after successful login"""
        try:
            next_url = self.request.GET.get('next')
            if next_url:
                return next_url
            # Default redirect to dashboard
            return '/dashboard/'
        except Exception:
            return '/dashboard/'
