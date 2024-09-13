from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from nltk.chat.util import Chat, reflections
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from django.core.cache import cache
from django.views import View
from rest_framework import viewsets
import requests
from .models import Webhook
from django.utils import timezone
from .models import ChatAnalytics
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json
import random
import re
from django.core.management.base import BaseCommand
from chatbot.models import Intent,Response



nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

class Command(BaseCommand):
    help = 'Populates initial chatbot data'
    def handle(self, *args, **kwargs):
        intents_data = {
            'greeting': 'hello,hi,hey,greetings',
            'farewell': 'bye,goodbye,see you,farewell',
            'thanks': 'thank,thanks,appreciate',
            'about': 'who,what,about,you',
            'help': 'help,assist,support',
            'default': '',
        }
        responses_data = {
            'greeting': ['Hello!', 'Hi there!', 'Greetings!'],
            'farewell': ['Goodbye!', 'See you later!', 'Take care!'],
            'thanks': ['You\'re welcome!', 'Glad I could help!', 'My pleasure!'],
            'about': ['I\'m a chatbot designed to assist you.', 'I\'m an AI assistant here to help with your questions.'],
            'help': ['How can I assist you?', 'What do you need help with?', 'I\'m here to help. What\'s your question?'],
            'default': ['I\'m not sure I understand. Could you rephrase that?', 'I don\'t have information about that. Is there something else I can help with?']
        }
        for intent_name, keywords in intents_data.items():
            intent, created = Intent.objects.get_or_create(name=intent_name, keywords=keywords)
            for response_text in responses_data[intent_name]:
                Response.objects.get_or_create(intent=intent, text=response_text)

            self.stdout.write(self.style.SUCCESS('Successfully populated chatbot data'))

# Simple intent recognition
intents = {
      'greeting': ['hello', 'hi', 'hey', 'greetings'],
    'farewell': ['bye', 'goodbye', 'see you', 'farewell'],
    'thanks': ['thank', 'thanks', 'appreciate'],
    'about': ['who', 'what', 'about', 'you'],
    'help': ['help', 'assist', 'support'],
}

responses = {
    'greeting': ['Hello!', 'Hi there!', 'Greetings!'],
    'farewell': ['Goodbye!', 'See you later!', 'Take care!'],
    'thanks': ['You\'re welcome!', 'Glad I could help!', 'My pleasure!'],
    'about': ['I\'m a chatbot designed to assist you.', 'I\'m an AI assistant here to help with your questions.'],
}
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return tokens

def get_intent(tokens):
    for intent, keywords in intents.items():
        if any(keyword in tokens for keyword in keywords):
            return intent
    return 'default'

def generate_response(message):
    tokens = preprocess_text(message)
    intent = get_intent(tokens)
    return random.choice(responses[intent])

@csrf_exempt
def chatfunc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            bot_response = generate_response(user_message)
            return JsonResponse({'response': bot_response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
def get_intent(tokens):
    for intent in Intent.objects.all():
        keywords = intent.keywords.split(',')
        if any(keyword.strip() in tokens for keyword in keywords):
            return intent.name
    return 'default'  


def generate_response(message):
    tokens = preprocess_text(message)
    intent = get_intent(tokens)
    responses = Response.objects.filter(intent__name=intent)
    if responses.exists():
        return random.choice(responses).text
    return random.choice(Response.objects.filter(intent__name='default'))

class ChatbotView(View):
    def post(self, request):
        user_message = request.POST.get('message', '')
        bot_response = "This is a test response"

        ChatMessage.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_response
        )

        return JsonResponse({'response': bot_response})
        # Check if response is in cache
        cache_key = f"chatbot_response_{user_message}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
             return JsonResponse({'response': cached_response})
        
        # If not in cache, generate response
        bot_response = self.generate_response(user_message)
        
        # Cache the response for 1 hour
        cache.set(cache_key, bot_response, 3600)
        
        return JsonResponse({'response': bot_response})
    
    #def generate_response(self, user_message):
        # Your chatbot logic here
     #    return "This is a test response"
    
class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer   



#nltk.download('punkt')

patterns = [
    (r'hi|hello|hey', ['Hello!', 'Hi there!', 'Hey!']),
    (r'how are you', ['I\'m doing well, thank you!', 'I\'m fine, how about you?']),
    (r'what is your name', ['My name is ChatBot.', 'I\'m ChatBot, nice to meet you!']),
    (r'bye|goodbye', ['Goodbye!', 'See you later!', 'Bye bye!']),
]

default_responses = [
     "I'm not sure I understand. Could you rephrase that?",
    "I don't have information about that. Is there something else I can help with?",
    "I'm still learning and don't have an answer for that yet. Can you try asking something else?"
]

 
def generate_response(message):
    # Convert message to lowercase for easier matching
    message = message.lower()
    
    # Check each pattern for a match
    for pattern, responses in patterns:
        if re.search(pattern, message):
           return random.choices(responses)
        
    return random.choices(default_responses)

chatbot = Chat(patterns, reflections)


logger = logging.getLogger(__name__)
def home(request):
    context = {'debug_message': 'Debug message from view'}
    return render(request, 'chatbot/home.html', context)

@login_required
def home(request):
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'chatbot/home.html', {'chat_messages': chat_messages})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})




@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(APIView):
    def post(self, request):
        user_message = request.POST.get('message', '')
        bot_response = "This is a test response"  #
        
        ChatMessage.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_response
        )

        return JsonResponse({'response': bot_response})
        print("ChatbotView post method called") 
        response = JsonResponse({'response': 'This is a test response'})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return Jsonresponse({'response': 'Test response'})

    def options(self, request):
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response
            #user_message = request.data.get('message', '')
           # try:
                #data = json.loads(request.body)
                #user_message = data.get('message', '')
            #except json.JSONDecodeError:
               # print("Failed to parse JSON")
                #return JsonResponse({'error': 'Invalid JSON'}, status=400)

            #print(f"Received message: {user_message}")  
       # logger.info(f"Received message: {user_message}")

           # bot_response = chatbot.respond(user_message)
        #logger.info(f"Bot response: {bot_response}")
            #print(f"Bot response: {bot_response}")
        # Save the message and response to the database
            #ChatMessage.objects.create(user_message=user_message, bot_response=bot_response)
        
                #return jsonResponse({'response': bot_response})
       # except Exception as e:
            #print(f"Error in ChatbotView: {str(e)}")
            #print(traceback.format_exc())
            #return jsonResponse({'error': str(e)}, status=500)

def home(request):
    return render(request, 'chatbot/home.html')



def send_webhook(message, response):
    webhooks = Webhook.objects.filter(is_active=True)
    for webhook in webhooks:
        try:
            requests.post(webhook.url, json={
                'message': message,
                'response': response
            })
        except requests.RequestException:
            # Log the error or handle it as appropriate
            pass

def update_analytics(user):
    today = timezone.now().date()
    analytics, created = ChatAnalytics.objects.get_or_create(date=today)
    analytics.total_chats += 1
    analytics.save()
    
    if created or user not in analytics.users.all():
        analytics.unique_users += 1
        analytics.users.add(user)
        analytics.save()

# Call update_analytics in your chat view or API

     #context = {'debug_message': 'Debug message from view'}
     #return render(request, 'chatbot/home.html', context)


    #def my_api_view(request):
        #return Response({'message': 'Success'}, status=200)

    #def api_endpoint(request):
    # Your API logic here
     #   return JsonResponse({"message": "API endpoint reached"})
def test_view(request):
    return HttpResponse("Test view is working!")