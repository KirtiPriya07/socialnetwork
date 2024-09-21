from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from api.models import UserMaster
from socialnetwork.paginations import SocialNetworkPaginationClass
from socialnetwork.responses import http_200_response, http_201_response, http_400_response, http_500_response
from api.users.serializers import UserRegistrationSerializer, UserLoginSerializer, UserLoginDataSerialzier, UserListSerializer
from api.permissions import IsReadOnly, IsWrite, IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated


# View for User Registration
class SignUp(ModelViewSet):
    http_method_names = ['post']
    permission_classes = (AllowAny,)
    queryset = UserMaster.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return http_201_response(message="User Registered Successfully!")
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(
                        message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}"
                    )
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))

# View for User Login
class Login(ModelViewSet):
    http_method_names = ['post']
    permission_classes = (AllowAny,)
    queryset = UserMaster.objects.all()
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data[1]
                login_data = UserLoginDataSerialzier(user).data
                return http_200_response(message="Login Success!", data=login_data)
            else:
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(
                        message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}"
                    )
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))

# View for finding and listing users with caching
class FindUsers(ModelViewSet):
    """This View lists all users, filters them based on name or email."""
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)
    queryset = UserMaster.objects.all()
    serializer_class = UserListSerializer

    def list(self, request, *args, **kwargs):
        try:
            users = UserMaster.objects.exclude(email=request.user.email)  # Exclude logged-in user
            search = request.query_params.get('search')  # Read from query parameter
            if search:
                users = users.filter(Q(name__icontains=search) | Q(email__iexact=search))  # Filter users based on name or email
            serializer = self.serializer_class(users, many=True)  # Serialize objects
            paginator = SocialNetworkPaginationClass()  # Initialize pagination class
            page = paginator.paginate_queryset(serializer.data, request) 
            return paginator.get_paginated_response(page)  # Return response in pages
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        pass  # This method is intentionally left blank


# Admin-only view for deleting users
class AdminDeleteUser(ModelViewSet):
    permission_classes = (IsAdmin,)  # Only 'Admin' users can delete users
    queryset = UserMaster.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return http_200_response(message="User Deleted Successfully")
        except Exception as e:
            return http_500_response(error=str(e))
