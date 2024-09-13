from django.urls import path,include
from rest_framework.routers import DefaultRouter
from.import views
#from .views import ChatbotView,chat_view

#app_name = 'chatbot'

router = DefaultRouter()
router.register(r'messages', views.ChatMessageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
   ##path('specific',views.specific,name='specific'),
    path('', views.home, name='home'),
    #path('api/', views.ChatbotView.as_view() , name='chatbot_api'),
    path('chatbot/api/', views.chatfunc, name='chatbot_api'),
    path('register/', views.register, name='register'),
    #path('api/endpoint/', views.api_endpoint, name='api_endpoint'),
    #path('test/', views.test_view, name='test_view'),
]
