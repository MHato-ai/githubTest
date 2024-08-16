from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token
from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from .models import Product
from .forms import ProductForm
from rest_framework import generics
from .serializers import UserSerializer
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


# Create your views here.

#Classess
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    
class ProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile  

def set_csrf_cookie(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["X-CSRFToken"] = get_token(request)
    return response


firstButtons = [
    {"label": "Create Account", "url": "/signup", "class": "btn"},
    {"label": "Login", "url": "/login", "class": "btn"},
]

@ensure_csrf_cookie 
def home(request):
    context = {"firstButtons": firstButtons}
    return render(request, "users/index.html", context)


@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body
            username = data.get("username")
            password = data.get("password")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            email = data.get("email")

            if not username or not password:
                return JsonResponse({'message': 'Username and password are required.'}, status=400)

            # if password != data.get("password_confirmation"):
            #     return JsonResponse({'message': 'Passwords do not match.'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'you have already signed up using this email'}, status=400)

            # Create the user
            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            return JsonResponse({'message': f'Hey {username}, your account was successfully created.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)

    return JsonResponse({'message': 'Method not allowed.'}, status=405)


buttons = [
    {"label": "Profile", "url": "/profile", "class": "btn"},
    {"label": "logout", "url": "/logout", "class": "btn"},
]


@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            userN = user.username
            messages.success(
                request, f"Hey {userN} you are authenticated to navigate to the page"
            )
            context = {"buttons": buttons}

            return render(request, "users/index.html", context)
        else:
            messages.error(request, "Invalid credentials")
            return redirect("home")
    return render(request, "users/login.html")


@login_required()
def profile(request):
    return render(request, "users/profile.html")


@csrf_exempt
@api_view(['POST', 'PUT','GET'])
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        # Check if the user already has a profile to prevent duplicates
        if hasattr(user, 'profile'):
            return Response({"detail": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new profile
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # Update an existing profile
        profile = get_object_or_404(Profile, user=user)  # Handle case where profile might not exist
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def contacts(request):
    return render(request, "users/contacts.html")


def logout(request):
    logout(request)
    return render(request, "users/logout.html")


def data(request):

    products = Product.objects.all()

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("data")
    else:
        form = ProductForm()

    # Query to get product categories and their respective counts (or any other data)
    data = Product.objects.values("category", "num_of_products").order_by("category")

    # Extracting categories and counts
    categories = [item["category"] for item in data]
    num_of_products = [item["num_of_products"] for item in data]

    # Pass the data to the template
    context = {
        "products": products,
        "form": form,
        "categories": json.dumps(categories),
        "counts": json.dumps(num_of_products),
    }
    return render(request, "users/charts.html", context)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
