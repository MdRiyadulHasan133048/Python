from rest_framework import serializers
from settings_app.models import Service, Promotion

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'isCustomizable', 'basePrice', 'hourNeeded','image']

class UserServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'image']

# .....................Promotion serrializer..........................

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title','description','image']
        
class PromotionEndUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion  
        fields = ['image'] 
# class UserProfileViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EndUser
#         fields = '__all__'