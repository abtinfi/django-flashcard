from django.shortcuts import render
from rest_framework.views import APIView, Response
from django.contrib.auth.models import User
from django.http import HttpResponse
from .serializers import *

class ApiRegister(APIView):
    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.POST)
        if ser_data.is_valid():
            User.objects.create_user(
                username=ser_data.validated_data["username"],
                email=ser_data.validated_data["email"],
                password=ser_data.validated_data["password"]
            )
            return Response(ser_data.data, status=201)
        
        # If the data is not valid, return the errors with a 400 status code
        return Response(ser_data.errors, status=400)
