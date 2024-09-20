from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.users.views import SignUp, Login, FindUsers
from api.friends.views import (
    SendFriendRequests, ViewPendingRequests, RejectFriendRequests, 
    AcceptFriendRequests, ViewFriends
)

# Create routers for users and friends
router = DefaultRouter()

# User routes
router.register('signup', SignUp, basename="signup")
router.register('login', Login, basename="login")
router.register('users', FindUsers, basename="users")

# Friend routes
router.register('send_request', SendFriendRequests, basename="send_request")
router.register('pending_requests', ViewPendingRequests, basename="pending_requests")
router.register('reject_request', RejectFriendRequests, basename="reject_request")
router.register('accept_request', AcceptFriendRequests, basename="accept_request")
router.register('view_friends', ViewFriends, basename="view_friends")

urlpatterns = [
    path("", include(router.urls)),
]
