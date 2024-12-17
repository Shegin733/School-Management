from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LoginView,SetNewPasswordView,PasswordForgotView,ResetPasswordView
from admin_dashboard.views import UserProfileView
router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    
    path('login/', LoginView.as_view(), name='login'),
    
    #forgot password
   
    path('password-forgot/', PasswordForgotView.as_view(), name='-password-forgot'),
    
]
