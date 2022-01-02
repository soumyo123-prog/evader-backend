from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from .models import Event, People, Expenditure
from django.contrib.auth import get_user_model
from datetime import datetime


class CreateEventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255, allow_blank=True)
    venue = serializers.CharField(max_length=255)
    time = serializers.DateTimeField()
    fireId = serializers.CharField(max_length=255)
    duration = serializers.IntegerField()

    def save(self):
        name = self.validated_data.get('name')
        description = self.validated_data.get('description', '')
        venue = self.validated_data.get('venue')
        time = self.validated_data.get('time')
        duration = self.validated_data.get('duration')
        fireId = self.validated_data.get('fireId')
        user = self.context["request"].user

        event = Event.objects.create(
            name=name, description=description,
            venue=venue, time=time,
            duration=duration,
            creator=user, fireId=fireId
        )
        event.save()
        return event


class FetchEventsSerializer(serializers.Serializer):
    def fetch(self):
        user = self.context["request"].user
        events = Event.objects.filter(creator=user)
        events_serialized = EventSerializer(events, many=True)
        return events_serialized


class FetchEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        id = data.get('id')
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)
        if not event:
            raise ValidationError(
                "User not permitted to access this event", status.HTTP_403_FORBIDDEN)
        return data

    def fetch(self):
        id = self.validated_data.get("id")
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)[0]
        event_serialized = EventSerializer(event)
        return event_serialized


class DeleteEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        id = data.get("id")
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)
        if not event:
            raise ValidationError(
                "User not permitted to access this event", status.HTTP_403_FORBIDDEN)
        return data

    def delete_event(self):
        id = self.validated_data.get("id")
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)[0]
        event.delete()


class UpdateEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    time = serializers.CharField()
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255, allow_blank=True)
    venue = serializers.CharField(max_length=255)

    def validate(self, data):
        id = data.get("id")
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)
        if not event:
            raise ValidationError(
                "User not permitted to access this event", status.HTTP_403_FORBIDDEN)

        event = event[0]
        currDate = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        eventDate = int(event.time.strftime("%Y%m%d%H%M%S"))
        if (eventDate < currDate):
            raise ValidationError(
                'Event cannot be modified because it is completed',
                status=status.HTTP_400_BAD_REQUEST)
        return data

    def update_event(self):
        time = datetime.strptime(self.validated_data.get(
            'time'), '%Y-%m-%dT%H:%M:%S.%fZ')
        name = self.validated_data.get('name')
        description = self.validated_data.get('description')
        venue = self.validated_data.get('venue')

        id = self.validated_data.get('id')
        user = self.context["request"].user
        event = Event.objects.filter(id=id, creator=user)[0]

        event.time = time
        event.name = name
        event.description = description
        event.venue = venue
        event.save()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'description',
                  'venue', 'time', 'fireId', 'duration']


class InvitationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        User = get_user_model()
        email = data.get('email')
        id = data.get('id')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User with this email does not exist',
                status.HTTP_404_NOT_FOUND)
        if not Event.objects.filter(id=id).exists():
            raise serializers.ValidationError(
                'Event with this id does not exist',
                status.HTTP_404_NOT_FOUND)
        if People.objects.filter(user__email=email, event__id=id).exists():
            raise serializers.ValidationError(
                'User is already invited to this event',
                status.HTTP_409_CONFLICT)

        eventDate = int(Event.objects.get(id=id).time.strftime("%Y%m%d%H%M%S"))
        currDate = int(datetime.now().strftime("%Y%m%d%H%M%S"))

        if (eventDate < currDate):
            raise serializers.ValidationError(
                'User cannot be invited because event is completed', status.HTTP_403_FORBIDDEN)

        return data

    def save(self):
        User = get_user_model()
        email = self.validated_data.get('email')
        id = self.validated_data.get('id')
        user = User.objects.filter(email=email)[0]
        event = Event.objects.get(id=id)
        invitation = People.objects.create(user=user, event=event)
        invitation.save()
        return invitation


class InvitedEventSerializer(serializers.Serializer):
    def fetch(self):
        user = self.context["request"].user
        invitations = People.objects.filter(user=user)

        if (invitations):
            invitedEvents = []
            for invitation in invitations:
                eventObj = invitation.event
                eventDict = EventSerializer(eventObj).data
                eventDict['status'] = invitation.status
                eventDict['invitedBy'] = f'{eventObj.creator.name} : {eventObj.creator.email}'
                invitedEvents.append(eventDict)
            return invitedEvents
        return []


class InvitationStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.IntegerField()

    def validate(self, data):
        id = data.get('id')
        status = data.get('status')
        user = self.context['request'].user

        if not People.objects.filter(event__id=id, user=user).exists():
            raise ValidationError(
                'User not permitted to modify this invitation',
                status.HTTP_403_FORBIDDEN)

        return data

    def save(self):
        id = self.validated_data.get('id')
        status = self.validated_data.get('status')
        user = self.context['request'].user

        invitation = People.objects.filter(event__id=id, user=user)[0]
        invitation.status = status
        invitation.save()


class GuestsSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        id = data.get('id')
        user = self.context['request'].user

        event = Event.objects.filter(id=id)
        if not event:
            raise ValidationError(
                'Event with this id does not exist', status.HTTP_404_NOT_FOUND)

        creator = event[0].creator
        invitation = People.objects.filter(event__id=id, user=user)
        if creator == user:
            return data
        if invitation:
            return data

        raise ValidationError(
            'User not permitted to see guest list of this event',
            status.HTTP_403_FORBIDDEN)

    def fetch(self):
        guests = People.objects.filter(event__id=self.validated_data.get('id'))
        guestsDictList = []
        if guests:
            for guest in guests:
                guestsDictList.append({
                    'id': guest.id,
                    'status': guest.status,
                    'name': guest.user.name,
                    'email': guest.user.email
                })
        return guestsDictList


class AddExpenditureSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    organization = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(default=0)
    unitPrice = serializers.IntegerField(default=0)

    def validate(self, data):
        id = data.get('id')
        if not Event.objects.filter(id=id).exists():
            raise ValidationError(
                'Event with this id does not exist', status.HTTP_404_NOT_FOUND)
        return data

    def save(self):
        id = self.validated_data.get('id')
        name = self.validated_data.get('name')
        organization = self.validated_data.get('organization')
        quantity = self.validated_data.get('quantity')
        unitPrice = self.validated_data.get('unitPrice')

        event = Event.objects.get(id=id)

        expenditure = Expenditure.objects.create(
            name=name,
            organization=organization,
            quantity=quantity,
            unitPrice=unitPrice,
            event=event
        )
        expenditure.save()
        return expenditure


class ExpenditureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenditure
        fields = ('id', 'name', 'organization', 'quantity', 'unitPrice',)
