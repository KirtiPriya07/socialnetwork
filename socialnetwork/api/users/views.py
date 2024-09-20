from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from api.models import UserMaster
from socialnetwork.paginations import SocialNetworkPaginationClass
from socialnetwork.responses import http_200_response, http_201_response, http_400_response, http_500_response
from api.users.serializers import UserRegistrationSerializer, UserLoginSerializer, UserLoginDataSerialzier, UserListSerializer

# View for User Registration
class SignUp(ModelViewSet):
    """ This View is Used to Register User using Name, Email and Password """
    http_method_names = ['post']
    permission_classes = (AllowAny,)
    queryset = UserMaster.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)  # deserializing payload
            if serializer.is_valid():  # validating the data
                serializer.save()  # saving the data to the DB
                return http_201_response(message="User Registered Successfully!")
            else:
                # Handling non-field-errors from serializer as well as custom validation errors
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
    """ This View is Used to Login Pre-Registered Users using email and password """
    http_method_names = ['post']
    permission_classes = (AllowAny,)
    queryset = UserMaster.objects.all()
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)  # deserializing payload
            if serializer.is_valid():  # validating data
                user = serializer.validated_data[1]  # extracting user instance returned from serializer
                login_data = UserLoginDataSerialzier(user).data  # passing instance to get login data like tokens
                return http_200_response(message="Login Success!", data=login_data)
            else:
                # Handling non-field-errors from serializer as well as custom validation errors
                if list(serializer.errors.keys())[0] != "error":
                    return http_400_response(
                        message=f"{list(serializer.errors.keys())[0]} : {serializer.errors[list(serializer.errors.keys())[0]][0]}"
                    )
                else:
                    return http_400_response(message=serializer.errors[list(serializer.errors.keys())[0]][0])
        except Exception as e:
            return http_500_response(error=str(e))


# View for finding and listing users
class FindUsers(ModelViewSet):
    """ This View lists all users, filters them based on name or email """
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)
    queryset = UserMaster.objects.all()
    serializer_class = UserListSerializer

    def list(self, request, *args, **kwargs):
        try:
            users = UserMaster.objects.exclude(email=request.user.email)  # excluding logged-in user
            search = request.query_params.get('search')  # reading search query parameter
            if search:
                users = users.filter(Q(name__icontains=search) | Q(email__iexact=search))  # filtering by name or email
            serializer = self.serializer_class(users, many=True)  # serializing objects
            paginator = SocialNetworkPaginationClass()  # initializing pagination class
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)  # returning response in pages
        except Exception as e:
            return http_500_response(error=str(e))

    def retrieve(self, request, *args, **kwargs):
        # This removes the retrieve method functionality, leaving it unimplemented.
        pass

