from rest_framework import serializers
import datetime
from api.models import FriendRequest

class SendFriendRequestsSerializer(serializers.ModelSerializer):
    sent_to = serializers.IntegerField(required=True)
    class Meta:
        model = FriendRequest
        fields = ['sent_to']
    def validate(self, attrs):
        sender = self.context.get("user")
        sent_to = attrs.get('sent_to')
        
        # Restrict user from sending request to himself/herself
        if sent_to == sender.id:
            raise serializers.ValidationError({'error':"You cannot send request to yourself!"})
        
        # Restrict user if request already sent and pending
        check_existing_request = FriendRequest.objects.filter(sent_to = sent_to, sent_by=sender,status="pending").exists()
        if check_existing_request:
            raise serializers.ValidationError({'error':"Friend Request already pending for selected user"})
        
        # Check if the request exists from the user to which the request is being sent / the recipient has already sent request
        check_existing_request = FriendRequest.objects.filter(sent_to = sender, sent_by_id=sent_to,status="pending").exists()
        if check_existing_request:
            raise serializers.ValidationError({'error':"Please accept/reject the pending request for this user"})
        
        # Apply limit on the number of requests to be sent in one minute
        time_limit = datetime.datetime.now() - datetime.timedelta(minutes=1)
        check_last_request = FriendRequest.objects.filter(sent_by = sender,created_on__gte= time_limit).count()
        if check_last_request >=3:
            raise serializers.ValidationError({'error':"You can only send upto 3 requests in one minute"})
        return attrs
    def create(self, validated_data):
        # create request is validated
        sent_to = validated_data.get("sent_to")
        sender = self.context.get('user')
        FriendRequest.objects.create(sent_to_id = sent_to,
                                        sent_by = sender,
                                        status="pending")
        return validated_data


class ViewPendingRequestsSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    sent_on = serializers.SerializerMethodField()
    class Meta:
        model = FriendRequest
        fields =['id','sent_by_id',"sender_name","sender_email",'sent_on']
    def get_sender_name(self,obj):
        return obj.sent_by.name
    def get_sender_email(self,obj):
        return obj.sent_by.email
    def get_sent_on(self,obj):
        return obj.created_on.strftime("%d-%m-%Y %I:%M:%S %p")


class AcceptFriendRequestsSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context.get("user")
        request_instance = self.instance
        if request_instance.sent_to != user:
            raise serializers.ValidationError({'error':"You cannot update the requests for other users"})
        if request_instance.status == "accepted":
            raise serializers.ValidationError({'error':"Request already accepted!"})
        return attrs
    def update(self,instance,validated_data):
        instance.status = "accepted"
        instance.save()
        return validated_data


class ViewFriendsSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    friends_since = serializers.SerializerMethodField()
    class Meta:
        model = FriendRequest
        fields =['id','sent_by_id',"sender_name","sender_email",'friends_since']
    def get_sender_name(self,obj):
        return obj.sent_by.name
    def get_sender_email(self,obj):
        return obj.sent_by.email
    def get_friends_since(self,obj):
        return obj.updated_on.strftime("%d-%m-%Y %I:%M:%S %p")