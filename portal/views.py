from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Application, Category
from .forms import RegisterForm, ApplicationForm, CategoryForm, StatusChangeForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


def index(request):
    completed_apps = Application.objects.filter(status='completed')[:4]
    in_progress_count = Application.objects.filter(status='in_progress').count()
    return render(request, 'index.html', {
        'completed_apps': completed_apps,
        'in_progress_count': in_progress_count,
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('profile')
        else:
            error = 'Неверный логин или пароль.'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    status_filter = request.GET.get('status', '')
    apps = Application.objects.filter(user=request.user)
    if status_filter:
        apps = apps.filter(status=status_filter)
    return render(request, 'profile.html', {
        'apps': apps,
        'status_filter': status_filter,
    })


@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.status = 'new'
            app.save()
            return redirect('profile')
    else:
        form = ApplicationForm()
    return render(request, 'create_app.html', {'form': form})


@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if app.status != 'new':
        return redirect('profile')
    if request.method == 'POST':
        app.delete()
        return redirect('profile')
    return render(request, 'delete_app.html', {'app': app})


@user_passes_test(is_admin)
def admin_dashboard(request):
    apps = Application.objects.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        cat_form = CategoryForm(request.POST)
        if cat_form.is_valid():
            cat_form.save()
            return redirect('admin_dashboard')
    else:
        cat_form = CategoryForm()
    return render(request, 'admin_dashboard.html', {
        'apps': apps,
        'categories': categories,
        'cat_form': cat_form,
    })


@user_passes_test(is_admin)
def delete_category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def change_status(request, pk):
    app = get_object_or_404(Application, pk=pk)
    if app.status != 'new':
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = StatusChangeForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = StatusChangeForm(instance=app)
    return render(request, 'change_status.html', {'form': form, 'app': app})