from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.cache.decorators import cache_response
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from api.permissions import IsAdmin, IsReadOnly, IsWrite
from api.models import FriendRequest
from socialnetwork.paginations import SocialNetworkPaginationClass
from api.friends.serializers import SendFriendRequestsSerializer, ViewPendingRequestsSerializer, AcceptFriendRequestsSerializer, ViewFriendsSerializer
from socialnetwork.responses import http_200_response, http_201_response, http_400_response, http_500_response

# View for Sending Friend Requests
class SendFriendRequests(ModelViewSet):
    """ This View is Used to Send Friend Requests"""
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()
    serializer_class = SendFriendRequestsSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'user': request.user})  # deserializing payload
            if serializer.is_valid():  # validating the data
                serializer.save()  # saving the friend request to the DB
                return http_201_response(message="Friend Request Sent Successfully!")
            else:
                # Handling non-field-errors from serializer as well as custom Validation errors from serializer
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))


# View for Viewing Pending Friend Requests with caching
class ViewPendingRequests(CacheResponseMixin, ModelViewSet):
    """ This View is Used to View Pending Friend Requests"""
    http_method_names = ['get']
    permission_classes = (IsAuthenticated, IsReadOnly )
    queryset = FriendRequest.objects.none()
    serializer_class = ViewPendingRequestsSerializer

    @cache_response()
    def list(self, request, *args, **kwargs):
        try:
            # Use select_related to fetch related user data in a single query
            pending_requests = FriendRequest.objects.filter(
                sent_to=request.user, status="pending"
            ).select_related('sent_by').order_by("-created_on")  # Assuming sent_by is a ForeignKey to User
            
            serializer = self.serializer_class(pending_requests, many=True)
            paginator = SocialNetworkPaginationClass()  # initializing pagination class
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)  # returning response in pages
        except Exception as e:
            return http_500_response(error=str(e))


    def retrieve(self, request, pk, *args, **kwargs):
        try:
            # filter the pending requests for authenticated user
            try:
                pending_request = FriendRequest.objects.get(id=int(pk))
            except FriendRequest.DoesNotExist:
                return http_400_response(message="Invalid ID")
            serializer = self.serializer_class(pending_request, many=False)
            return http_200_response(message="Data fetched Successfully!", data=serializer.data)
        except Exception as e:
            return http_500_response(error=str(e))


# View for Rejecting Friend Requests
class RejectFriendRequests(ModelViewSet):
    """ This View is Used to Reject Friend Requests"""
    http_method_names = ['delete']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()

    def destroy(self, request, pk, *args, **kwargs):
        try:
            # Use select_related to fetch related user data if needed
            request_instance = FriendRequest.objects.select_related('sent_by', 'sent_to').get(id=int(pk))

            if request_instance.sent_to != request.user:
                return http_400_response(message="You cannot delete the requests for other users")

            request_instance.delete()
            return http_200_response(message="Friend Request Rejected Successfully!")
        except FriendRequest.DoesNotExist:
            return http_400_response(message="Invalid ID")
        except Exception as e:
            return http_500_response(error=str(e))



# View for Accepting Friend Requests
class AcceptFriendRequests(ModelViewSet):
    """ This View is Used to Accept Friend Requests"""
    http_method_names = ['put']
    permission_classes = (IsAuthenticated,)
    queryset = FriendRequest.objects.none()
    serializer_class = AcceptFriendRequestsSerializer

    def update(self, request, pk, *args, **kwargs):
        try:
            # Use select_related to fetch related user data
            request_instance = FriendRequest.objects.select_related('sent_by', 'sent_to').get(id=int(pk))

            serializer = self.serializer_class(request_instance, data=request.data, context={'user': request.user})
            if serializer.is_valid():
                serializer.save()  # Accept the friend request in the DB
                return http_201_response(message="Friend Request Accepted Successfully!")
            else:
                # Handling non-field-errors from serializer as well as custom validation errors
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}")
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except FriendRequest.DoesNotExist:
            return http_400_response(message="Invalid ID")
        except Exception as e:
            return http_500_response(error=str(e))



# View for Viewing Friends with caching
class ViewFriends(CacheResponseMixin, ModelViewSet):
    """ This View is Used to View Friend Listing"""
    http_method_names = ['get']
    permission_classes = (IsAuthenticated, IsReadOnly)
    queryset = FriendRequest.objects.none()
    serializer_class = ViewFriendsSerializer

    @cache_response()
    def list(self, request, *args, **kwargs):
        try:
            # Use select_related to optimize fetching users
            friends = FriendRequest.objects.filter(
                Q(sent_to=request.user) | Q(sent_by=request.user), status="accepted"
            ).select_related('sent_to', 'sent_by').order_by("-updated_on")
            
            serializer = self.serializer_class(friends, many=True)
            paginator = SocialNetworkPaginationClass()  # initializing pagination class
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)  # returning response in pages
        except Exception as e:
            return http_500_response(error=str(e))


    def retrieve(self, request, pk, *args, **kwargs):
        try:
            # filter the pending requests for authenticated user
            try:
                friend = FriendRequest.objects.get(id=int(pk))
            except FriendRequest.DoesNotExist:
                return http_400_response(message="Invalid ID")
            serializer = self.serializer_class(friend, many=False)
            return http_200_response(message="Data fetched Successfully!", data=serializer.data)
        except Exception as e:
            return http_500_response(error=str(e))
