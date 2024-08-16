from django.urls import path
from users import views
from users import admin
from django.contrib.auth import views as auth_view
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, ProfileDetail
from .views import UserList

router = DefaultRouter()
router.register(r'items', ItemViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("profile/", views.profile_view, name="profile"),
    path("contacts/", views.contacts, name="contacts"),
    path("data/", views.data, name="data"),
    path('logout/', auth_view.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    path('', include(router.urls)),
    path('users/', UserList.as_view(), name='user-list'),
    path('profile/', ProfileDetail.as_view(), name='profile-detail'),
    
]
