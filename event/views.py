from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions
from django.contrib.auth import get_user_model
from .models import Event, Expenditure, People
from .serializers import (
    AddExpenditureSerializer,
    CreateEventSerializer,
    DeleteEventSerializer,
    EventSerializer,
    ExpenditureSerializer,
    FetchEventSerializer,
    FetchEventsSerializer,
    GuestsSerializer,
    InvitationSerializer,
    InvitedEventSerializer,
    InvitationStatusSerializer,
    UpdateEventSerializer
)

from datetime import datetime

# Create your views here.


class CreateEventView(GenericAPIView):
    """
    post:
        Creates an event with the given data if valid and returns the details of the event.
        Otherwise returns a 400 bad request.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = CreateEventSerializer

    def post(self, request, *args, **kwargs):
        time = datetime.strptime(request.data.get(
            'time'), '%Y-%m-%dT%H:%M:%S.%fZ')
        request.data['time'] = time
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        event_dict = EventSerializer(event)
        return Response(data=event_dict.data, status=status.HTTP_201_CREATED)


class FetchEventsView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FetchEventsSerializer
    queryset = Event.objects.all()

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        events = serializer.fetch()
        return Response(data=events.data, status=status.HTTP_200_OK)


class FetchEventView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FetchEventSerializer
    queryset = Event.objects.all()

    def get(self, request, pk):
        request.data['id'] = pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.fetch()
        return Response(data=event.data, status=status.HTTP_200_OK)


class DeleteEventView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeleteEventSerializer
    queryset = Event.objects.all()

    def delete(self, request, pk):
        request.data['id'] = pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delete_event()
        return Response(data={}, status=status.HTTP_200_OK)


class UpdateEventView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateEventSerializer
    queryset = Event.objects.all()

    def put(self, request, pk):
        request.data['id'] = pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_event()
        return Response(data={}, status=status.HTTP_200_OK)


class InvitePeopleView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = People.objects.all()
    serializer_class = InvitationSerializer

    def post(self, request, *args, **kwargs):
        request.data['id'] = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            error = serializer.errors.get('non_field_errors')[0]
            return Response(data={'error': error}, status=status.HTTP_404_NOT_FOUND)
        invitation = serializer.save()
        invitationDict = {
            'id': invitation.id,
            'status': invitation.status,
            'name': invitation.user.name,
            'email': invitation.user.email
        }
        return Response(data=invitationDict, status=status.HTTP_200_OK)


class FetchInvitedEventsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = InvitedEventSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        invitations = serializer.fetch()
        return Response(data=invitations, status=status.HTTP_200_OK)


class FetchInvitedEventView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    queryset = People.objects.all()

    def get(self, request, *args, **kwargs):
        invitation = People.objects.filter(
            event__id=kwargs.get('pk'), user=request.user)
        if invitation:
            invitation = invitation[0]
            event = self.get_serializer(invitation.event).data
            event['status'] = invitation.status
            event['invitedBy'] = (
                f'{invitation.event.creator.name} : {invitation.event.creator.email}')
            return Response(data=event, status=status.HTTP_200_OK)
        return Response(
            data={'error': 'User is not permitted to view this event'},
            status=status.HTTP_403_FORBIDDEN)


class SetInvitationStatusView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationStatusSerializer
    queryset = People.objects.all()

    def post(self, request, *args, **kwargs):
        request.data['id'] = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={}, status=status.HTTP_200_OK)
        return Response(
            data={'error': 'User not permitted to modify this invitation'},
            status=status.HTTP_403_FORBIDDEN)


class FetchGuestsView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GuestsSerializer
    queryset = People.objects.all()

    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        request.data['id'] = id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            guestsDictList = serializer.fetch()
            return Response(data=guestsDictList, status=status.HTTP_200_OK)
        errors = serializer.errors
        code = status.HTTP_400_BAD_REQUEST
        if errors['non_field_errors']:
            if errors['non_field_errors'][0].code == 404:
                code = status.HTTP_404_NOT_FOUND
            else:
                code = status.HTTP_403_FORBIDDEN
            return Response(data=[], status=code)
        return Response(data=[], status=status.HTTP_400_BAD_REQUEST)


class GuestView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GuestsSerializer
    queryset = People.objects.all()

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if People.objects.filter(id=id).exists():
            invitation = People.objects.filter(id=id)[0]
            if invitation.event.creator == request.user:
                invitation.delete()
                return Response(data={}, status=status.HTTP_200_OK)
            return Response(
                data={'error': 'User is not permitted to delete this invitation'},
                status=status.HTTP_403_FORBIDDEN)

        return Response(
            data={'error': 'Invitation with this id does not exist'},
            status=status.HTTP_404_NOT_FOUND)


class ExpenditureView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddExpenditureSerializer
    queryset = Expenditure.objects.all()

    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        event = Event.objects.filter(id=id, creator=request.user)
        if event:
            event = event[0]
            expenditures = Expenditure.objects.filter(event=event)
            if expenditures:
                serializer = ExpenditureSerializer(expenditures, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=[], status=status.HTTP_200_OK)
        return Response(
            data={'error': 'User not permitted to view expenditure of this event'},
            status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        request.data['id'] = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            expenditure = serializer.save()
            expenditureDict = ExpenditureSerializer(expenditure)
            return Response(data=expenditureDict.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        code = status.HTTP_400_BAD_REQUEST
        if errors['non_field_errors']:
            code = status.HTTP_404_NOT_FOUND
            return Response(data={}, status=code)
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        expenditure = Expenditure.objects.filter(id=id)
        if expenditure:
            expenditure = expenditure[0]
            if expenditure.event.creator == request.user:
                expenditure.delete()
                return Response(data={}, status=status.HTTP_200_OK)
            return Response(
                data={'error': 'User is not permitted to delete this expenditure'},
                status=status.HTTP_403_FORBIDDEN)
        return Response(
            data={'error': 'Expenditure with this id does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )


class UsageView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get(self, request, *args, **kwargs):
        created = 0
        invited = 0
        if Event.objects.filter(creator=request.user).exists():
            created = Event.objects.filter(creator=request.user).count()
        if People.objects.filter(user=request.user).exists():
            invited = People.objects.filter(user=request.user).count()

        return Response(
            data={'created': created, 'invited': invited},
            status=status.HTTP_200_OK)
