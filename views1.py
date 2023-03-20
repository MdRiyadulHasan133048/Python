from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse, Http404
import requests, json, hashlib, datetime, random
from abode_app.models import EndUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser  
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status    
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticated 
from api_app import serializers
from django.conf import settings
from django.core.mail import send_mail 

####################  Here write all api views  #######################

# Create your views here.
def get_tokens_for_user(get_user): 
    refresh = RefreshToken.for_user(get_user)

    return  str(refresh.access_token)
     
  
class NewUserSignUp(APIView): 
    # permission_classes = [IsAuthenticated]
    serializers_class = serializers.EndUserSerializer
    
    def post(self, request): 
        try:
            get_respons = json.loads(request.body.decode('utf-8')) 
            password   = get_respons['password']
            md5_obj   = hashlib.md5(password.encode())
            enc_pass  = md5_obj.hexdigest()  
            text_id = get_respons['email']
            # Check Existing user 
            chk_user = EndUser.objects.filter(email=get_respons['email']).first() 
            print("chk_user", chk_user)
            if not chk_user: 
                get_user = EndUser.objects.create(
                    firstName = get_respons['first_name'], lastName = get_respons['last_name'],email = get_respons['email'], 
                    country_code = get_respons['country_code'], phone = get_respons['phone'], password = enc_pass, textid=text_id, 
                )
                if get_user:
                    print("get_user", get_user) 
                    token = get_tokens_for_user(get_user) 
                    serializer = self.serializers_class(get_user, many=False)
                    return Response({'message': "Success","token":token, 'get_data':serializer.data},status=status.HTTP_201_CREATED)
                
            else:
                return Response({'message': "Exist User"}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            print(e)
            return Response({'message': "something wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
#........................ User Login Via Email .............................   

class UserLoginViaEmail(APIView):
    def post(self, request):
        try:
            # Get API Respons 
            get_respons = json.loads(request.body.decode('utf-8')) 
            
            get_user = EndUser.objects.filter(email = get_respons['email']).first()
            if get_user:  
                return Response({'message': "Please Enter your password"}, status=status.HTTP_200_OK)         
            else:
                return Response({'message': "We could not find your email! Please sign up."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': "something wrong"}, status=status.HTTP_400_BAD_REQUEST)
      

# .............................User Login via Password after Email validation........................
  
class UserLoginViaPassword(APIView):
    def post(self, request):  
        # Get API Respons 
        get_respons = json.loads(request.body.decode('utf-8')) 
         
        password   = get_respons['password']
        md5_obj   = hashlib.md5(password.encode())
        enc_pass  = md5_obj.hexdigest()
           
        get_user = EndUser.objects.filter(email = get_respons['email'], password = enc_pass).first()
         
        if get_user:
            token = get_tokens_for_user(get_user) 
            return Response({'message': "Login Successful.", "token": token}, status=status.HTTP_200_OK)         
        else:
            return Response({'message': "Login Failed"}, status=status.HTTP_400_BAD_REQUEST)


# .......................Create OTP For User Login .......................................................
     
class CreateOtpForUserLogin(APIView):
    def post(self, request):  
        # Get API Respons
        try: 
            get_respons = json.loads(request.body.decode('utf-8'))
            print("res", get_respons)  
            
            get_user = EndUser.objects.filter(email = get_respons['email']).first()
            print("get_user", get_user)
            if get_user:
                if get_user.phone:
                    phone = get_user.phone
                    otp_code = random.randint(100000,999999)
                    print(otp_code)
                    subject = 'Passcode for Login'
                    message = "Your Passcode OTP code is "+str(otp_code)+", Please enter your OTP code for login"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [get_user.email]
                    send_mail( subject, message, email_from, recipient_list)
                                    
                    EndUser.objects.filter(email = get_respons['email']).update(otp_code = otp_code)
                    return Response({"message": "Your OTP Code is " + str(otp_code) }, status=status.HTTP_200_OK)
                    
                    #return Response({"Message": "We sent an OPT code your email and phone. Thanks"}, status=status.HTTP_201_CREATED)     
                else:
                    return Response({"We couldn't find your email/phone number"}, status=status.HTTP_400_BAD_REQUEST)     
                        
            else:
                return Response({'message': "We couldn't find your email"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': "something wrong"}, status=status.HTTP_400_BAD_REQUEST)

# ..............................User Login via OTP Verification....................................
   
class UserLoginViaOTP(APIView):
    serializers_class = serializers.EndUserSerializer
    def post(self, request):  
        # Get API Respons 
        get_respons = json.loads(request.body.decode('utf-8'))  
        
        get_user = EndUser.objects.filter(email = get_respons['email']).first()
        
        if get_user:
            if get_user.otp_code == int(get_respons['otp_code']): 
                token = get_tokens_for_user(get_user) 
                serializer = self.serializers_class(get_user, many=False)
                
                return Response({"Message":"Log In Successfull", "Token":token, "data": serializer.data}, status=status.HTTP_200_OK)     
            else:
                
                return Response({"We couldn't find your pho"}, status=status.HTTP_200_OK)     
                    
        else:
            return Response({'message': "We couldn't find your email"}, status=status.HTTP_400_BAD_REQUEST)

#.......................................... User Profile View......................................... 
  
class UserProfileView(APIView):  
    serializers_class = serializers.UserProfileViewSerializer
    
    def get(self, request):
        try:
            get_email =  json.loads(request.body.decode('utf-8'))  
            get_data = EndUser.objects.get(email=get_email['email'])
            if get_data:   
                token = get_tokens_for_user(get_data) 
                serializer = self.serializers_class(get_data, many=False) 
            
                return Response({"Success": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"Message":"User Not Found" }, status=status.HTTP_400_BAD_REQUEST) 
        except:
            return Response({'message': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# ........................................User Change Password via Email .....................................................

class UserChangePasswordViaEmail(APIView):    
    def get(self, request):
        try:
            get_respons =  json.loads(request.body.decode('utf-8'))  
             
             
            get_data = EndUser.objects.filter(email=get_respons['email']).first()
            if get_data: 
                return Response({"Message": "Enter Your Password"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Invalide email."}, status=status.HTTP_400_BAD_REQUEST)
                
        except:
            return Response({'message': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# ..............................User Change Password via Password .....................................

class UserChangePasswordViaPassword(APIView):    
    def post(self, request):
        try:
            get_respons =  json.loads(request.body.decode('utf-8'))  
             
            password   = get_respons['password']
            md5_obj   = hashlib.md5(password.encode())
            enc_pass  = md5_obj.hexdigest()
            
            get_data = EndUser.objects.filter(email=get_respons['email']).first()
            if get_data:
                EndUser.objects.filter(email=get_respons['email']).update(
                    password = enc_pass
                )  
                return Response({"Message": "Password Changed Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)
                
        except:
            return Response({'message': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# User Reset Password
class ResetPasswordViaEmail(APIView):    
    def get(self, request):
        try:
            get_respons =  json.loads(request.body.decode('utf-8'))   
            get_user = EndUser.objects.get(email=get_respons['email'])
            if get_user:
                return Response({"Message": "Please Set Your New Password"}, status=status.HTTP_200_OK)
        
        except:
            return Response({'message': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# User Reset Password
class ResetPassword(APIView):    
    def post(self, request):
        try:
            get_respons =  json.loads(request.body.decode('utf-8'))   
            get_user = EndUser.objects.get(email=get_respons['email'])
            password   = get_respons['password']
            md5_obj   = hashlib.md5(password.encode())
            enc_pass  = md5_obj.hexdigest() 
            if get_user:
                EndUser.objects.filter(email=get_respons['email']).update(password=enc_pass)
                
                return Response({"Message": "Password Reset Successfull"}, status=status.HTTP_200_OK)
        
            else:
                return Response({'message': "Something Went Wrong"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

#........................ EndUser Forgot Password Via Send OTP.......................

class sendOtpForforgotPassword(APIView): 
    def post(self, request):
        try: 
            # Get data from apps request
            data = json.loads(request.body.decode('utf-8'))
            print("data", data)
 
            chk_EndUser = EndUser.objects.filter(email = data['email']).first()
            print("User",chk_EndUser )  

            if chk_EndUser:  
                otp_code = random.randint(100000, 999999)
                subject = 'Passcode for Login'
                message = "Your Passcode OTP code is "+str(otp_code)+", Please enter your OTP code for login"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [chk_EndUser.email]
                send_mail( subject, message, email_from, recipient_list) 
                # Here append Send email code for OTP Send.
                EndUser.objects.filter(email = data['email']).update(otp_code = otp_code)
                return Response({"message": "Your OTP Code is "+str(otp_code) }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "EndUser Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            print(e)
            return Response({"message": "EndUser Forgot Password Failed"}, status=status.HTTP_400_BAD_REQUEST)
        

#........................ EndUser Forgot Password Via Otp.......................

class confirmOtpForForgotPassword(APIView): 
    def post(self, request):
        try: 
            # Get data from apps request
            data = json.loads(request.body.decode('utf-8'))
            print("data", data)
            get_otp = str(data['otp_code'])
            if len(get_otp) == 6: 
                print("otp", get_otp)
                chk_EndUser = EndUser.objects.filter(email = data['email'], otp_code = data['otp_code']).first()  

                if chk_EndUser: 
                    print("hj",chk_EndUser.otp_code)  
                    EndUser.objects.filter(email = data['email']).update(otp_code = 0)
                    return Response({"message": "OTP Successful, Please set your new password."}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "EndUser Not Found"}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(e)
            return Response({"message": "EndUser Forgot Password Failed"}, status=status.HTTP_400_BAD_REQUEST)
        



#........................ EndUsers Reset Password .......................

class EndUserPasswordReset(APIView): 
    def post(self, request):
        try: 
            # Get data from apps request
            data = json.loads(request.body.decode('utf-8')) 
            md5_pass   = hashlib.md5(data['password'].encode()).hexdigest() # Generate MD5 password
            chk_EndUser = EndUser.objects.filter(email = data['email']).first()
            
            if chk_EndUser:
                EndUser.objects.filter(email = data['email']).update(password=md5_pass)
                return Response({"message": "Password Reset Successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "EndUser Not Found"}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(e)
            return Response({"message": "EndUser Forgot Password Failed"}, status=status.HTTP_400_BAD_REQUEST)
         