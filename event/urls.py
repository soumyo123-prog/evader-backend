from django.urls import path
from .views import (
    CreateEventView,
    DeleteEventView,
    FetchEventsView,
    FetchEventView,
    GuestView,
    InvitePeopleView,
    FetchInvitedEventsView,
    FetchInvitedEventView,
    SetInvitationStatusView,
    FetchGuestsView,
    ExpenditureView,
    UpdateEventView,
    UsageView,
)

urlpatterns = [
    path('create/', CreateEventView.as_view()),
    path('fetch/', FetchEventsView.as_view()),
    path('fetch/invited', FetchInvitedEventsView.as_view()),
    path('fetch/<int:pk>/', FetchEventView.as_view()),
    path('delete/<int:pk>/', DeleteEventView.as_view()),
    path('update/<int:pk>/', UpdateEventView.as_view()),
    path('fetch/<int:pk>/guests/', FetchGuestsView.as_view()),
    path('fetch/invited/<int:pk>/', FetchInvitedEventView.as_view()),
    path('invite/<int:pk>/', InvitePeopleView.as_view()),
    path('invitation/status/<int:pk>/', SetInvitationStatusView.as_view()),
    path('invitation/remove/<int:pk>/', GuestView.as_view()),
    path('expenditure/<int:pk>/', ExpenditureView.as_view()),
    path('usage/', UsageView.as_view())
]
