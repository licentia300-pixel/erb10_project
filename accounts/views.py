from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from listings.models import Bookmark  # ← 新增这一行


def register(request):
    if request.method == 'POST':
        # 1. 从 POST 中获取表单数据（新增 username）
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # 2. 基础数据校验
        if not username or not first_name or not last_name or not email or not password or not password2:
            messages.error(request, "所有字段都必须填写。")
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, "两次输入的密码不一致。")
            return render(request, 'accounts/register.html')

        # 校验用户名是否被占用
        if User.objects.filter(username=username).exists():
            messages.error(request, "该用户名已被占用，请换一个。")
            return render(request, 'accounts/register.html')

        # 校验邮箱是否被占用
        if User.objects.filter(email=email).exists():
            messages.error(request, "该邮箱已被注册，请直接登录。")
            return render(request, 'accounts/register.html')

        # 3. 创建用户（使用用户填写的 username，而不是 email）
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # 4. 注册后自动登录
        login(request, user)
        messages.success(request, f"欢迎 {first_name}！注册成功。")

        # 5. 跳转到仪表板
        return redirect('accounts:dashboard')

    # GET 请求
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"欢迎回来，{user.first_name or user.username}！")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "用户名或密码错误。")
            return render(request, 'accounts/login.html')
    else:
        return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    # 获取当前用户的所有收藏
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('wallpaper')
    context = {
        'user': request.user,
        'bookmarks': bookmarks,
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "您已成功登出。")
    return redirect('accounts:login')