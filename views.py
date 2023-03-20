from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests, json
from . import models
from django.views.decorators.csrf import csrf_exempt
import datetime

# from rest_framework import generics

from django.http import Http404
from django.core.cache import cache
from django.conf import settings
import hashlib
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from settings_app.models import Service, Promotion
from abode_app.serializers import ServiceSerializer, UserServiceSerializer, PromotionSerializer,PromotionEndUserSerializer

from abode_app.serializers import UserServiceSerializer
from rest_framework import generics
from rest_framework import mixins
from rest_framework.generics import ListAPIView

# from abode_app.pagination import CustomPageNumberPagination
# from rest_framework.pagination import LimitOffsetPagination
from .paginations import CategorySetPagination
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(get_user):
    refresh = RefreshToken.for_user(get_user)

    return str(refresh.access_token)


# CACHE_TTL = getattr(settings,'CACHE_TTL', DEFAULT_TIMEOUT)


class ServiceEndUser(APIView):
    serializers_class = ServiceSerializer

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            print(data)
            text_id = data["title"]
            print(text_id)
            temp = text_id.replace(" ", "")
            if temp:
                service = Service.objects.create(
                    textId=temp,
                    title=data["title"],
                    isCustomizable=data["isCustomizable"],
                    basePrice=data["basePrice"],
                    hourNeeded=data["hourNeeded"],
                    image = data["image"],
                )
                if service:
                    print("service ...")
        except Exception as e:
            print(e)
            return Response(
                {"message": "EndUser Forgot Password Failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

#..................................... service category creation....................................................
class ServiceCategory(APIView):
    # queryset = Service.objects.all()
    # serializer_class = ServiceSerializer
    
    def post(self, request, format=None):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
#............................. Promotion creation ....................................  

class PromotionCreation(APIView):
    def post(self, request, format=None):
        serializer = PromotionSerializer(data=request.data)
        
        if serializer.is_valid():
            
            obj = dict(serializer.validated_data)
            text_id = obj['title'].replace(" ","")
            # for data in dict(serializer.validated_data):
            # print(".......",obj['title'])
            # for key,value in obj.items():
            #     print(key, "  ", value)
            # textId = text_id
             
            serializer.save(textId = text_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# ................................Get Promotion view....................................

class PromotionEndUserView(generics.ListAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionEndUserSerializer
    # pagination_class = CategorySetPagination      

# class ServiceEndUserView(APIView):
#     serializers_class = UserServiceSerializer
#     def get(self, request):
#         try:
#             service_list= Service.objects.all().values()
#             if service_list:
#                 serializer =  self.serializers_class(service_list, many =False)

#             print(service_list)
#             return Response({"Message":"Success", "data":serializer.data}, status=status.HTTP_200_OK)
#             #print("User", user)
#         except Exception as e:
#             print(e)

# class CategoryEndUserView(generics.GenericAPIView):
#     serializer_class = UserServiceSerializer
#     pagination_class = CustomPagination
#     #pagination_class = CustomPageNumberPagination
#     #print(pagination_class)
#     def get(self, request):

#         try:
#             queryset = Service.objects.all().values()
#             # print("Pagination class: ", pagination_class)

#             if queryset:
#                 serializer =self.serializer_class(queryset,many = True)
#                 #token =get_tokens_for_user(queryset)
#                 return Response({"Message":"Successful",  "data":serializer.data}, status=status.HTTP_200_OK)

#         except Exception as e:
#             print(e)

# ..............................EndUser Category view...............................

class CategoryEndUserView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = UserServiceSerializer
    pagination_class = CategorySetPagination


# admin Login
def adminlogin(request):
    if request.method == "POST":
        get_data = models.UserList.objects.filter(
            email=request.POST.get("user_email"),
            password=request.POST.get("password"),
            status=True,
        ).first()
        if get_data:
            request.session["user_id"] = get_data.id
            request.session["user_email"] = get_data.email

            return redirect("/dashboard/")

    return render(request, "login.html")


def admin_dashboard(request):
    return render(request, "dashboard.html")


def user_list(request):
    user_list = models.UserList.objects.all().order_by("-id")
    total_user = user_list

    page = request.GET.get("page", 1)
    paginator = Paginator(user_list, 10)
    try:
        user_list = paginator.page(page)

    except PageNotAnInteger:
        user_list = paginator.page(1)
    except EmptyPage:
        user_list = paginator.page(paginator.num_pages)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if is_ajax:
        get_status = request.POST.get("status")
        user_id = int(request.POST.get("user_id"))
        display_message = "Active"
        if get_status == "True":
            display_message = "Inactive"
            models.UserList.objects.filter(id=user_id).update(status=False)

        elif get_status == "False":
            display_message = "Active"
            models.UserList.objects.filter(id=user_id).update(status=True)

        return JsonResponse(display_message, safe=False)

    return render(
        request,
        "user_list.html",
        {"user_list": user_list, "total_user": len(total_user)},
    )
