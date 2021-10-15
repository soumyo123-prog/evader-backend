from django.urls import path
from .views import LoginView, ProfileView

urlpatterns = [
    path('login/', view=LoginView.as_view()),
    path('profile/', view=ProfileView.as_view()),
]
