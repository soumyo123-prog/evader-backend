from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from .models import Event, People
from django.contrib.auth import get_user_model


class EventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255, allow_blank=True)
    venue = serializers.CharField(max_length=255)
    time = serializers.DateTimeField()
    fireId = serializers.CharField(max_length=255)

    def save(self, **kwargs):
        name = self.validated_data.get('name')
        description = self.validated_data.get('description', '')
        venue = self.validated_data.get('venue')
        time = self.validated_data.get('time')
        fireId = self.validated_data.get('fireId')
        user = self.context["request"].user

        event = Event.objects.create(
            name=name, description=description,
            venue=venue, time=time,
            creator=user, fireId=fireId
        )
        event.save()
        return event


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'venue', 'time', 'fireId', ]


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


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = ['id', 'status', ]


class InvitedEventSerializer(serializers.Serializer):
    def fetch(self):
        user = self.context["request"].user
        invitations = People.objects.filter(user=user)

        if (invitations):
            invitedEvents = []
            for invitation in invitations:
                eventObj = invitation.event
                eventDict = EventsSerializer(eventObj).data
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
                    'status': guest.status,
                    'name': guest.user.name,
                    'email': guest.user.email
                })
        return guestsDictList
