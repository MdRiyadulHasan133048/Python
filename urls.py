from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    
    path('dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('adminlogin/', views.adminlogin, name="adminlogin"), 
    path('user-list/', views.user_list, name="user_list"), 
    path('ServiceEndUser', views.ServiceEndUser.as_view(), name="ServiceEndUser"), 
    path('CategoryEndUserView', views.CategoryEndUserView.as_view(), name="CategoryEndUserView"),       
    path('ServiceCategory', views.ServiceCategory.as_view(), name="ServiceCategory"),       
    path('PromotionCreation', views.PromotionCreation.as_view(), name="PromotionCreation"),       
    path('PromotionEndUserView', views.PromotionEndUserView.as_view(), name="PromotionEndUserView"),       
    
]