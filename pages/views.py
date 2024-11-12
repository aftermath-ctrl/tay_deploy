from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView




# views.py
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .forms import TextGenerationForm
from accounts.models import ChatHistory
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_text_view(request):
    if request.method == "POST":
        form = TextGenerationForm(request.POST)
        
        if form.is_valid():
            # Extract cleaned data from the form
            text_input = form.cleaned_data["text_input"]
            max_tokens = form.cleaned_data["max_tokens"]
            bad_words = form.cleaned_data["bad_words"]
            stop_words = form.cleaned_data["stop_words"]

            # Data to send to the internal model endpoint
            payload = {
                "text_input": text_input,
                "max_tokens": max_tokens,
                "bad_words": bad_words,
                "stop_words": stop_words
            }
            
            # Call the internal model API
            try:
                response = requests.post(
                    "http://54.204.29.1:8000/v2/models/ensemble/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response_data = response.json()
                print("ayee",response_data)
                generated_text = response_data.get("generated_text", "")
            except Exception as e:
                print(f"Error calling the model API: {e}")
                generated_text = "Error generating text"

            return JsonResponse({"generated_text": generated_text})

    else:
        form = TextGenerationForm()
    
    return render(request, "generate_text.html", {"form": form})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from accounts.forms import TextGenerationForm

from django.views.decorators.csrf import csrf_protect


 
@csrf_protect
def handle_post2(request):
    if request.method == "POST":
        form = TextGenerationForm(request.POST)
        if form.is_valid():
            # Extract form data
            text_input = form.cleaned_data['text_input']
            max_tokens = form.cleaned_data['max_tokens']
            bad_words = form.cleaned_data['bad_words']
            stop_words = form.cleaned_data['stop_words']
            pad_id = form.cleaned_data['pad_id']
            end_id = form.cleaned_data['end_id']
            
            payload = {
                "text_input": text_input,
                "max_tokens": max_tokens,
                "bad_words": bad_words,
                "stop_words": stop_words,
                "pad_id": pad_id,
                "end_id": end_id
            }
            
            try:
                response = requests.post(
                    "http://54.204.29.1:8000/v2/models/llama-2-7b/generate",
                    json=payload,
                )
                response.raise_for_status()
                response_data = response.json()
                
                if 'text_output' in response_data:
                    # Get the response text
                    result_text = response_data['text_output']
                    
                    # Remove the input question
                    result_text = result_text.replace(text_input, '')
                    
                    # Clean up formatting
                    result_text = result_text.strip()  # Remove leading/trailing whitespace
                    result_text = result_text.replace('\n', ' ')  # Replace newlines with spaces
                    
                    # Split by period and take the first complete sentence
                    sentences = result_text.split('.')
                    result_text = sentences[0].strip() + '.'

                       # Save the chat history
                    ChatHistory.objects.create(
                        user_input=text_input,
                        bot_response=result_text
                    )
                    
                    
                    if not result_text:  # If empty after cleaning
                        result_text = "No additional text generated."
                else:
                    result_text = "No generated text found."
                    
                return JsonResponse({"result_text": result_text})
                
            except requests.RequestException as e:
                print("Error calling the model API:", e)
                return JsonResponse({"error": "Failed to generate text from model API"}, status=500)
                
        print("Form Errors:", form.errors)
        return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)






def chat_history(request):
    if request.method == "GET":
        chat_logs = ChatHistory.objects.order_by('-timestamp')
        data = [{"user_input": log.user_input, "bot_response": log.bot_response} for log in chat_logs]
        return JsonResponse(data, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)


def index(request):
    form = TextGenerationForm()
    return render(request, '../templates/index.html', {'form': form})


class HomePageView(TemplateView):
	template_name = "home.html"


from django.shortcuts import render



from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import requests

@csrf_protect
def handle_post(request):
    if request.method == "POST":
        # Check authentication status and handle rate limiting for anonymous users
        if not request.user.is_authenticated:
            client_ip = request.META.get('REMOTE_ADDR')
            cache_key = f'prompt_count_{client_ip}'
            prompt_count = cache.get(cache_key, 0)
            
            if prompt_count >= 5:
                return JsonResponse({
                    "error": "prompt_limit_reached",
                    "message": "You have reached the limit of 5 prompts. Please sign in to continue."
                }, status=403)
            
            # Increment prompt count for anonymous users
            cache.set(cache_key, prompt_count + 1, timeout=86400)  # 24 hour timeout

        form = TextGenerationForm(request.POST)
        if form.is_valid():
            # Extract form data
            text_input = form.cleaned_data['text_input']
            max_tokens = form.cleaned_data['max_tokens']
            bad_words = form.cleaned_data['bad_words']
            stop_words = form.cleaned_data['stop_words']
            pad_id = form.cleaned_data['pad_id']
            end_id = form.cleaned_data['end_id']
            
            payload = {
                "text_input": text_input,
                "max_tokens": max_tokens,
                "bad_words": bad_words,
                "stop_words": stop_words,
                "pad_id": pad_id,
                "end_id": end_id
            }
            
            try:
                response = requests.post(
                    "http://54.204.29.1:8000/v2/models/llama-2-7b/generate",
                    json=payload,
                )
                response.raise_for_status()
                response_data = response.json()
                
                if 'text_output' in response_data:
                    # Get the response text
                    result_text = response_data['text_output']
                    
                    # Remove the input question
                    result_text = result_text.replace(text_input, '')
                    
                    # Clean up formatting
                    result_text = result_text.strip()  # Remove leading/trailing whitespace
                    result_text = result_text.replace('\n', ' ')  # Replace newlines with spaces
                    
                    # Split by period and take the first complete sentence
                    sentences = result_text.split('.')
                    result_text = sentences[0].strip() + '.'
                    
                    # Save the chat history with user association if authenticated
                    chat_history = ChatHistory.objects.create(
                        user_input=text_input,
                        bot_response=result_text,
                        user=request.user if request.user.is_authenticated else None
                    )
                    
                    if not result_text:  # If empty after cleaning
                        result_text = "No additional text generated."
                else:
                    result_text = "No generated text found."
                    
                return JsonResponse({
                    "result_text": result_text,
                    "remaining_prompts": None if request.user.is_authenticated else 
                        5 - (cache.get(f'prompt_count_{request.META.get("REMOTE_ADDR")}', 1))
                })
                
            except requests.RequestException as e:
                print("Error calling the model API:", e)
                return JsonResponse({"error": "Failed to generate text from model API"}, status=500)
                
        print("Form Errors:", form.errors)
        return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

# Optional helper view to check remaining prompts
def check_remaining_prompts(request):
    if request.user.is_authenticated:
        return JsonResponse({"unlimited": True})
    
    client_ip = request.META.get('REMOTE_ADDR')
    prompt_count = cache.get(f'prompt_count_{client_ip}', 0)
    remaining = max(5 - prompt_count, 0)
    
    return JsonResponse({
        "remaining_prompts": remaining,
        "total_allowed": 5
    })