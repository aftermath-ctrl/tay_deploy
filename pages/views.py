from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView




# views.py
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .forms import TextGenerationForm
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


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel, ValidationError
from accounts.models import PromptFormat
import requests

# Define the Pydantic model for validation
class PromptRequest(BaseModel):
    text_input: str
    max_tokens: int = 20
    bad_words: str = ""
    stop_words: str = ""

@csrf_exempt
def generate_response(request):
    url = "http://54.204.29.1:8000/v2/models/ensemble/generate"

    if request.method == "POST":
        # Parse form data into dictionary
        form_data = {
            "text_input": request.POST.get("text_input", ""),
            "max_tokens": int(request.POST.get("max_tokens", 20)),
            "bad_words": request.POST.get("bad_words", ""),
            "stop_words": request.POST.get("stop_words", ""),
        }

        try:
            # Validate form data using Pydantic
            data = PromptRequest(**form_data)

            # Prepare the payload for the API call
            payload = data.dict()

            # Make the API call
            response = requests.post(url, json=payload, verify=False, timeout=10)
            result = response.json()
            print(result)

            # If this is an AJAX request, return JSON directly
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"generated_text": result.get("generated_text", "")})

            # For non-AJAX, render the full template with context
            return render(request, "generate_prompt.html", {
                "response": result.get("generated_text", ""),
                "request_data": form_data
            })

        except ValidationError as e:
            # Handle validation errors and return them in context
            errors = e.errors()
            return render(request, "generate_prompt.html", {
                "errors": errors,
                "request_data": form_data
            })

    # Render template on GET request
    return render(request, "generate_prompt.html")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from accounts.forms import TextGenerationForm

from django.views.decorators.csrf import csrf_protect


 
@csrf_protect
def handle_post(request):
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


def index(request):
    form = TextGenerationForm()
    return render(request, 'index.html', {'form': form})


class HomePageView(TemplateView):
	template_name = "home.html"


