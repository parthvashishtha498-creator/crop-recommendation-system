from django.contrib import messages
from django.contrib.auth import authenticate, login , logout 
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.contrib.auth.models import User 
from .models import *
# Create your views here.
from django.contrib.auth.models import User
from .models import Pridiction

def home(request):

    total_users = User.objects.filter(is_staff=False).count()

    total_predictions = Pridiction.objects.count()

    context = {
        "total_users": total_users,
        "total_predictions": total_predictions,
    }

    return render(request, "home.html", context)


def signup(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Password Match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        # Username Exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        # Email Exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        # Create User
        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password1,
        )

        messages.success(request, "Account created successfully.")
        return redirect("login")

    context = {
        "total_users": User.objects.filter(is_staff=False).count(),
        "total_predictions": Pridiction.objects.count(),
    }

    return render(request, "signup.html", context)

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin
            if user.is_staff:
                return redirect("/admin/")

            # Normal User
            return redirect("prediction")

        else:
            messages.error(request, "Invalid Username or Password.")

    return render(request, "login.html")

import joblib
import numpy as np
from .models import Pridiction as Prediction
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "recommender",
    "ml",
    "Crop_Recommendation_model.pkl"
)

model = joblib.load(MODEL_PATH)
scaler = joblib.load(os.path.join(
    settings.BASE_DIR,
    "recommender",
    "ml",
    "Crop_Recommendation_scaler.pkl"
))
@login_required(login_url="login")
def prediction(request):

    if request.method == "POST":

        N = float(request.POST.get("N"))
        P = float(request.POST.get("P"))
        K = float(request.POST.get("K"))
        temperature = float(request.POST.get("temperature"))
        humidity = float(request.POST.get("humidity"))
        ph = float(request.POST.get("ph"))
        rainfall = float(request.POST.get("rainfall"))

        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        data_scaled = scaler.transform(data)

        predicted_label = model.predict(data_scaled)[0]

        Prediction.objects.create(
            user=request.user,
            N=N,
            P=P,
            K=K,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            predicted_label=predicted_label
        )

        messages.success(request, f"Recommended Crop: {predicted_label}")

        return render(request, "prediction.html", {
            "prediction": predicted_label
        })

    return render(request, "prediction.html")


from .models import Pridiction

@login_required(login_url="login")
def history(request):

    predictions = Pridiction.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "history.html", {
        "predictions": predictions
    })



from .models import Pridiction

@login_required(login_url="login")
def profile(request):

    predictions = Pridiction.objects.filter(user=request.user)

    total_predictions = predictions.count()

    latest_prediction = predictions.order_by("-id").first()

    context = {
        "total_predictions": total_predictions,
        "latest_prediction": latest_prediction,
    }

    return render(request, "profile.html", context)
@login_required(login_url="login")
def edit_profile(request):

    if request.method == "POST":

        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")

        request.user.save()

        if "image" in request.FILES:

            profile = request.user.profile
            profile.image = request.FILES["image"]
            profile.save()

        messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    return render(request, "edit_profile.html")


from django.contrib.auth import logout
from django.contrib import messages


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from django.shortcuts import render

from .models import Pridiction


@staff_member_required(login_url="admin_login")
def dashboard(request):

    # ==========================================
    # Dashboard Cards
    # ==========================================

    total_users = User.objects.filter(is_staff=False).count()

    total_admins = User.objects.filter(is_staff=True).count()

    total_predictions = Pridiction.objects.count()

    # ==========================================
    # Crop Distribution (Pie Chart)
    # ==========================================

    crop_counts = (
        Pridiction.objects
        .values("predicted_label")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # ==========================================
    # Prediction Trend (Line Chart)
    # ==========================================

    prediction_trend = (
        Pridiction.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # ==========================================
    # Average Soil Nutrients (Bar Chart)
    # ==========================================

    avg = Pridiction.objects.aggregate(

        avg_n=Avg("N"),

        avg_p=Avg("P"),

        avg_k=Avg("K")

    )

    # ==========================================
    # Recent Predictions
    # ==========================================

    recent_predictions = (
        Pridiction.objects
        .select_related("user")
        .order_by("-created_at")
    )

    context = {

        # Summary Cards

        "total_users": total_users,

        "total_admins": total_admins,

        "total_predictions": total_predictions,

        # Charts

        "crop_counts": crop_counts,

        "prediction_trend": prediction_trend,

        "avg_n": round(avg["avg_n"] or 0, 2),

        "avg_p": round(avg["avg_p"] or 0, 2),

        "avg_k": round(avg["avg_k"] or 0, 2),

        # Table

        "recent_predictions": recent_predictions,

    }

    return render(request, "dashboard.html", context)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect


@login_required(login_url="admin_login")
def users(request):

    if not request.user.is_staff:
        return redirect("prediction")

    search = request.GET.get("search", "")

    user_list = User.objects.filter(is_staff=False)

    if search:
        user_list = user_list.filter(
            username__icontains=search
        )

    user_list = user_list.annotate(
        prediction_count=Count("pridictions")
    ).order_by("-date_joined")

    context = {

        "users": user_list,

        "search": search,

        "total_users": user_list.count(),

    }

    return render(request, "users.html", context)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
@login_required(login_url="login")
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Password changed successfully.")

            return redirect("profile")

        else:

            messages.error(request, "Please correct the errors below.")

    else:

        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {
        "form": form
    })
    
from django.contrib.auth import authenticate, login
from django.contrib import messages

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            messages.success(request, "Welcome Admin!")

            return redirect("dashboard")

        messages.error(request, "Invalid admin credentials.")

    return render(request, "admin_login.html")

from django.shortcuts import get_object_or_404

@login_required(login_url="admin_login")
def user_details(request, user_id):

    if not request.user.is_staff:
        return redirect("prediction")

    selected_user = get_object_or_404(
        User,
        id=user_id
    )

    predictions = selected_user.pridictions.all()

    context = {

        "selected_user": selected_user,

        "predictions": predictions,

    }

    return render(
        request,
        "user_details.html",
        context
    )
    
def terms_privacy(request):
    return render(request, "terms_privacy.html")

from django.contrib.auth.models import User
from django.http import HttpResponse

