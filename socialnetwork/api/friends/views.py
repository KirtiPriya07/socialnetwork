from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from api.permissions import IsAdmin, IsReadOnly, IsWrite, IsNotBlocked
from api.models import FriendRequest, BlockedUser, UserMaster
from socialnetwork.paginations import SocialNetworkPaginationClass
from api.friends.serializers import (
    SendFriendRequestsSerializer,
    ViewPendingRequestsSerializer,
    AcceptFriendRequestsSerializer,
    ViewFriendsSerializer,
    BlockUserSerializer,
    UnblockUserSerializer,
    UserProfileSerializer
)
from socialnetwork.responses import http_200_response, http_201_response, http_400_response, http_500_response


# View for Sending Friend Requests (No Cache)
class SendFriendRequests(ModelViewSet):
    """ This View is Used to Send Friend Requests"""
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()
    serializer_class = SendFriendRequestsSerializer

    def create(self, request, *args, **kwargs):
        try:
            blocked_users = BlockedUser.objects.filter(blocked_by=request.user).values_list('blocked_user_id', flat=True)
            recipient_id = request.data.get('sent_to')
            
            if recipient_id in blocked_users:
                return http_400_response(message="You cannot send a friend request to a blocked user.")
            
            # Check if the recipient has blocked the user
            if BlockedUser.objects.filter(blocked_by=recipient_id, blocked_user=request.user).exists():
                return http_400_response(message="You cannot send a friend request to a user who has blocked you.")
            
            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                serializer.save()
                return http_201_response(message="Friend Request Sent Successfully!")
            else:
                return http_400_response(message=serializer.errors)
        except Exception as e:
            return http_500_response(error=str(e))


# View for Viewing Pending Friend Requests with caching
class ViewPendingRequests(CacheResponseMixin, ModelViewSet):
    """ This View is Used to View Pending Friend Requests"""
    http_method_names = ['get']
    permission_classes = (IsAuthenticated, IsReadOnly)
    queryset = FriendRequest.objects.none()
    serializer_class = ViewPendingRequestsSerializer

    @cache_response()
    def list(self, request, *args, **kwargs):
        try:
            pending_requests = FriendRequest.objects.filter(
                sent_to=request.user, status="pending"
            ).select_related('sent_by').order_by("-created_on")
            
            serializer = self.serializer_class(pending_requests, many=True)
            paginator = SocialNetworkPaginationClass()
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)
        except Exception as e:
            return http_500_response(error=str(e))

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            pending_request = FriendRequest.objects.get(id=int(pk))
            serializer = self.serializer_class(pending_request, many=False)
            return http_200_response(message="Data fetched Successfully!", data=serializer.data)
        except FriendRequest.DoesNotExist:
            return http_400_response(message="Invalid ID")
        except Exception as e:
            return http_500_response(error=str(e))


# View for Rejecting Friend Requests (No Cache)
class RejectFriendRequests(ModelViewSet):
    """ This View is Used to Reject Friend Requests"""
    http_method_names = ['delete']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()

    def destroy(self, request, pk, *args, **kwargs):
        try:
            request_instance = FriendRequest.objects.select_related('sent_by', 'sent_to').get(id=int(pk))

            if request_instance.sent_to != request.user:
                return http_400_response(message="You cannot delete the requests for other users")

            request_instance.delete()
            return http_200_response(message="Friend Request Rejected Successfully!")
        except FriendRequest.DoesNotExist:
            return http_400_response(message="Invalid ID")
        except Exception as e:
            return http_500_response(error=str(e))


# View for Accepting Friend Requests (No Cache)
class AcceptFriendRequests(ModelViewSet):
    """ This View is Used to Accept Friend Requests"""
    http_method_names = ['put']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()
    serializer_class = AcceptFriendRequestsSerializer

    def update(self, request, pk, *args, **kwargs):
        try:
            request_instance = FriendRequest.objects.select_related('sent_by', 'sent_to').get(id=int(pk))

            serializer = self.serializer_class(request_instance, data=request.data, context={'user': request.user})
            if serializer.is_valid():
                serializer.save()
                return http_201_response(message="Friend Request Accepted Successfully!")
            else:
                return http_400_response(message=serializer.errors)
        except FriendRequest.DoesNotExist:
            return http_400_response(message="Invalid ID")
        except Exception as e:
            return http_500_response(error=str(e))


# View for Viewing Friends with caching
class ViewFriends(CacheResponseMixin, ModelViewSet):
    """ This View is Used to View Friend Listing"""
    http_method_names = ['get']
    permission_classes = (IsAuthenticated, IsReadOnly, IsNotBlocked)
    queryset = FriendRequest.objects.none()
    serializer_class = ViewFriendsSerializer

    @cache_response()
    def list(self, request, *args, **kwargs):
        try:
            friends = FriendRequest.objects.filter(
                Q(sent_to=request.user) | Q(sent_by=request.user), status="accepted"
            ).select_related('sent_to', 'sent_by').order_by("-updated_on")
            
            serializer = self.serializer_class(friends, many=True)
            paginator = SocialNetworkPaginationClass()
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)
        except Exception as e:
            return http_500_response(error=str(e))


class UserProfileView(RetrieveAPIView):
    """ This View allows users to view profiles """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            profile_user_id = kwargs.get('user_id')

            # Check if user is blocked or has blocked the profile user
            if BlockedUser.objects.filter(blocked_by=profile_user_id, blocked_user=user.id).exists() or \
               BlockedUser.objects.filter(blocked_by=user.id, blocked_user=profile_user_id).exists():
                return Response({"message": "You cannot view this profile. You are blocked or have blocked this user."}, 
                                status=status.HTTP_403_FORBIDDEN)

            # Proceed with profile view logic if no blocking is involved
            profile_user = UserMaster.objects.get(id=profile_user_id)
            serializer = UserProfileSerializer(profile_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserMaster.DoesNotExist:
            return Response({"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# View for Blocking a User (No Cache)
class BlockUser(ModelViewSet):
    """ This View is Used to Block a User """
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)
    queryset = BlockedUser.objects.none()
    serializer_class = BlockUserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                serializer.save()
                return http_201_response(message="User Blocked Successfully!")
            else:
                return http_400_response(message=serializer.errors)
        except Exception as e:
            return http_500_response(error=str(e))


# View for Unblocking a User (No Cache)
class UnblockUser(ModelViewSet):
    """ This View is Used to Unblock a User """
    http_method_names = ['delete']
    permission_classes = (IsAuthenticated,)
    queryset = BlockedUser.objects.none()

    def destroy(self, request, *args, **kwargs):
        try:
            serializer = UnblockUserSerializer(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                blocked_user_id = serializer.validated_data['blocked_user_id']
                BlockedUser.objects.filter(blocked_by=request.user, blocked_user_id=blocked_user_id).delete()
                return http_200_response(message="User Unblocked Successfully!")
            else:
                return http_400_response(message=serializer.errors)
        except Exception as e:
            return http_500_response(error=str(e))
