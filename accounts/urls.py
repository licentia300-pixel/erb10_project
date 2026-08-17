from django.urls import path
from . import views

app_name = 'accounts'  # 命名空间（与项目路由中的 namespace='accounts' 对应）

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]