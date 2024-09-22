from rest_framework import serializers
import datetime
from api.models import FriendRequest, BlockedUser,UserMaster,FriendRequest

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
            raise serializers.ValidationError({'error': "You cannot send a request to yourself!"})

        # Restrict user if request already sent and pending
        if FriendRequest.objects.filter(sent_to=sent_to, sent_by=sender, status="pending").exists():
            raise serializers.ValidationError({'error': "Friend Request already pending for selected user"})

        # Check if the recipient has sent a request to the sender
        if FriendRequest.objects.filter(sent_to=sender, sent_by_id=sent_to, status="pending").exists():
            raise serializers.ValidationError({'error': "Please accept/reject the pending request for this user"})

        # Apply limit on the number of requests to be sent in one minute
        time_limit = datetime.datetime.now() - datetime.timedelta(minutes=1)
        if FriendRequest.objects.filter(sent_by=sender, created_on__gte=time_limit).count() >= 3:
            raise serializers.ValidationError({'error': "You can only send up to 3 requests in one minute"})

        # Check if the recipient is blocked by the sender
        blocked_users = BlockedUser.objects.filter(blocked_by=sender).values_list('blocked_user_id', flat=True)
        if sent_to in blocked_users:
            raise serializers.ValidationError("You cannot send a friend request to a blocked user.")

        # Check if the sender is blocked by the recipient
        if BlockedUser.objects.filter(blocked_by=sent_to, blocked_user=sender).exists():
            raise serializers.ValidationError("You cannot send a friend request to a user who has blocked you.")

        return attrs

    def create(self, validated_data):
        sent_to = validated_data.get("sent_to")
        sender = self.context.get('user')
        FriendRequest.objects.create(sent_to_id=sent_to, sent_by=sender, status="pending")
        return validated_data


class ViewPendingRequestsSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    sent_on = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'sent_by_id', "sender_name", "sender_email", 'sent_on']

    def get_sender_name(self, obj):
        return obj.sent_by.name

    def get_sender_email(self, obj):
        return obj.sent_by.email

    def get_sent_on(self, obj):
        return obj.created_on.strftime("%d-%m-%Y %I:%M:%S %p")


class AcceptFriendRequestsSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context.get("user")
        request_instance = self.instance
        if request_instance.sent_to != user:
            raise serializers.ValidationError({'error': "You cannot update the requests for other users"})
        if request_instance.status == "accepted":
            raise serializers.ValidationError({'error': "Request already accepted!"})
        return attrs

    def update(self, instance, validated_data):
        instance.status = "accepted"
        instance.save()
        return validated_data


class ViewFriendsSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    friends_since = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'sent_by_id', "sender_name", "sender_email", 'friends_since']

    def get_sender_name(self, obj):
        return obj.sent_by.name

    def get_sender_email(self, obj):
        return obj.sent_by.email

    def get_friends_since(self, obj):
        return obj.updated_on.strftime("%d-%m-%Y %I:%M:%S %p")

class UserProfileSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()
    blocked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = UserMaster
        fields = ['id', 'username', 'email', 'profile_picture', 'is_blocked', 'blocked_by_user']

    def get_is_blocked(self, obj):
        user = self.context['request'].user
        return BlockedUser.objects.filter(blocked_by=user, blocked_user=obj).exists()

    def get_blocked_by_user(self, obj):
        user = self.context['request'].user
        return BlockedUser.objects.filter(blocked_by=obj, blocked_user=user).exists()


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = ['blocked_user']

    def validate_blocked_user(self, value):
        """Prevent users from blocking themselves or blocking already blocked users."""
        user = self.context['user']
        if user.id == value:
            raise serializers.ValidationError("You cannot block yourself.")
        if BlockedUser.objects.filter(blocked_by=user, blocked_user=value).exists():
            raise serializers.ValidationError("This user is already blocked.")
        return value

    def create(self, validated_data):
        blocked_by = self.context['user']
        blocked_user = validated_data['blocked_user']
        block_instance, created = BlockedUser.objects.get_or_create(blocked_by=blocked_by, blocked_user=blocked_user)
        return block_instance


class UnblockUserSerializer(serializers.Serializer):
    blocked_user_id = serializers.IntegerField()

    def validate_blocked_user_id(self, value):
        """Check if the user is actually blocked."""
        user = self.context['user']
        if not BlockedUser.objects.filter(blocked_by=user, blocked_user_id=value).exists():
            raise serializers.ValidationError("User is not blocked.")
        return value
