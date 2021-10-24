from django.urls import path
from .views import (
    CreateEventView,
    FetchEventsView,
    FetchEventView,
    InvitePeopleView,
    FetchInvitedEventsView,
    FetchInvitedEventView,
    SetInvitationStatusView,
    FetchGuestsView,
    ExpenditureView
)

urlpatterns = [
    path('create/', CreateEventView.as_view()),
    path('fetch/', FetchEventsView.as_view()),
    path('fetch/invited', FetchInvitedEventsView.as_view()),
    path('fetch/<int:pk>/', FetchEventView.as_view()),
    path('fetch/<int:pk>/guests/', FetchGuestsView.as_view()),
    path('fetch/invited/<int:pk>/', FetchInvitedEventView.as_view()),
    path('invite/<int:pk>/', InvitePeopleView.as_view()),
    path('invitation/status/<int:pk>/', SetInvitationStatusView.as_view()),
    path('expenditure/<int:pk>/', ExpenditureView.as_view()),
    path('delete/<int:pk>/', FetchEventView.as_view()),
]
