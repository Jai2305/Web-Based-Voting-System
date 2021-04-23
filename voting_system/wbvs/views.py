from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from django.contrib.auth.hashers import make_password

from .models import Result, User, Booth, Candidate, Voter, VotingList, History

from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
import re
 

class RegisterForm(forms.Form):
    first_name = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-group form-control', 'autofocus type':'text'}), max_length=10)
    last_name = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-group form-control', 'autofocus type':'text'}), max_length=10)
    email = forms.EmailField(label = "",widget= forms.TextInput(attrs={'placeholder':'Email', 'class':'form-group form-control', 'autofocus type':'text'}))
    password = forms.CharField(label = "",widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-group form-control', 'autofocus type':'text'}))
    confirmation = forms.CharField(label = "",widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password', 'class':'form-group form-control', 'autofocus type':'text'}))
    image = forms.ImageField(label = "Choose your Profile Photo")


class LoginForm(forms.Form):
    email = forms.EmailField(label = "",widget= forms.TextInput(attrs={'placeholder':'Email', 'class':'form-group form-control', 'autofocus type':'text', 'margin' : '20px'}))
    password = forms.CharField(label = "",widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-group form-control', 'autofocus type':'text'}))


class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label = "",widget=forms.PasswordInput(attrs={'placeholder':'New Password', 'class':'form-group form-control', 'autofocus type':'text'}))
    confirmation = forms.CharField(label = "",widget=forms.PasswordInput(attrs={'placeholder':'Confirm New Password', 'class':'form-group form-control', 'autofocus type':'text'}))


class AdminForm1(forms.Form):
    title = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Title'}))
    description = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Description'}))


class AdminForm2(forms.Form):
    name = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Candidate Name'}))
    des = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Candidate Description'}))
    cand_im = forms.ImageField(label = "Image")


class VoterForm1(forms.Form):
    boothID = forms.CharField(label = "",widget= forms.TextInput(attrs={'placeholder':'Enter Booth ID'}))


def index(request):
    return render(request, "wbvs/index.html")


def homepage(request):
    return render(request, "wbvs/homepage.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        username = re.findall('(\S+)@', email)
        username = str(username[0]) + "@user"
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return render(request, "wbvs/homepage.html", {
                "success_login" : True
            })
        else:
            return render(request, "wbvs/login.html", {
                "message": "Invalid email and/or password.",
                "login_form" : LoginForm(request.POST)
            })
    else:
        return render(request, "wbvs/login.html", {
            "login_form" : LoginForm()
        })


def logout_view(request):
    logout(request)
    return render(request, "wbvs/index.html", {
        "success_logout" : True
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            image = form.cleaned_data["image"]

            username = re.findall('(\S+)@', email)
            username = str(username[0]) + "@user"

            # Ensure password matches confirmation
            password = form.cleaned_data["password"]
            confirmation = form.cleaned_data["confirmation"]
            if password != confirmation:
                return render(request, "wbvs/register.html", {
                    "message": "Passwords must match.",
                    "register_form" : RegisterForm(request.POST)
                })

            # Attempt to create new user user.image.url
            try:
                user = User.objects.create_user(email = email, password = password, first_name = first_name, last_name = last_name, username = username, image = image)
                user.save()
            except IntegrityError:
                return render(request, "wbvs/register.html", {
                    "message": "Email already in use.",
                    "register_form" : RegisterForm(request.POST)
                })
            login(request, user)
            return render(request, "wbvs/homepage.html", {
                "success_register" : True
            })
    else:
        return render(request, "wbvs/register.html", {
            "register_form" : RegisterForm()
        })


def adminpage1(request):
    var = uuid.uuid4().hex[:10].upper()
    var = var + "@booth"
    Booth.objects.create(boothID = var, active = True, admin = request.user)
    return render(request, "wbvs/adminpage1.html", {
        "boothID" : var,
        "adminform1" : AdminForm1()
    })


def adminform1(request, Id):
    user_var = User.objects.get(pk = request.user.id)
    if request.method == "POST":
        data = AdminForm1(request.POST)
        if data.is_valid():
            ti = data.cleaned_data["title"]
            des = data.cleaned_data["description"]
            Booth.objects.filter(boothID = Id, active = True).update(title = ti, admin = user_var, description = des)
            History.objects.create(user = request.user, boothID = Id, role = "Voting Admin", result_declared = False, result = "", active = True, voting_status = "NA")
            return HttpResponseRedirect(reverse("adminpage2", args=(Id, )))
        else:
            return HttpResponseRedirect(reverse("homepage"))


def adminpage2(request, Id):
    candidate_var = Candidate.objects.filter(boothID = Id).all()
    if request.method == "POST":
        form = AdminForm2(request.POST, request.FILES)
        if form.is_valid():
            var = uuid.uuid4().hex[:6].upper()
            var = var + "@candidate"

            name = form.cleaned_data["name"]
            des = form.cleaned_data["des"]
            cand_image = form.cleaned_data["cand_im"]
            
            Candidate.objects.create(boothID = Id, candidateID = var, candidateName = name, description = des, image = cand_image)
            return HttpResponseRedirect(reverse("adminpage2", args=(Id,)))
    else:
        return render(request, "wbvs/adminpage2.html", {
            "boothID" : Id,
            "candidate_list" : candidate_var,
            "adminform2" : AdminForm2(),
        })


def adminpage3(request, Id):
    voter_list = Voter.objects.filter(boothID = Id).all()
    if request.method == "POST":
        voter_var = User.objects.get(pk = int(request.POST["foo"]))
        request_rply = int(request.POST["request_rply"])
        Voter.objects.filter(voterID = voter_var).update(allowed = request_rply)
        if (request_rply == -1):
            Voter.objects.filter(voterID = voter_var, boothID = Id).update(voting_status = "Rejected")
            History.objects.filter(user = voter_var, boothID = Id).update(voting_status = "Rejected")
        elif (request_rply == 1):
            History.objects.filter(user = voter_var, boothID = Id).update(voting_status = "Not Voted")
        return HttpResponseRedirect(reverse("adminpage3", args=(Id, )))

    candidate_var = Candidate.objects.filter(boothID = Id).all()
    if len(candidate_var) < 2:
        return render(request, "wbvs/adminpage2.html", {
            "cnadidate_count_warning" : True,
            "boothID" : Id,
            "candidate_list" : candidate_var,
            "adminform2" : AdminForm2(),
        })

    return render(request, "wbvs/adminpage3.html", {
        "boothID" : Id,
        "voter_list" : voter_list,
        "total_requests" : len(Voter.objects.filter(boothID = Id).all()),
        "approved_requests" : len(Voter.objects.filter(boothID = Id , allowed = 1).all()),
        "denied_requests" : len(Voter.objects.filter(boothID = Id , allowed = -1).all()),
        "voted_votes" : len(Voter.objects.filter(boothID = Id , allowed = 1, voting_status = "Voted").all()),
        "pending_votes" : len(Voter.objects.filter(boothID = Id , allowed = 1, voting_status = "Not Voted").all()),
    })


def voterpage1(request):
    if request.method == "POST":
        data = VoterForm1(request.POST)
        if data.is_valid():
            boo = data.cleaned_data["boothID"]
            try: 
                booth = Booth.objects.get(boothID = boo, active = True)
            except:
                return render(request, "wbvs/homepage.html", {
                    "failed_booth_find" : True
                })
            History.objects.create(user = request.user, boothID = boo, role = "Voter", result_declared = False, result = "", active = True, voting_status = "W8ing_4_req")
            return render(request, "wbvs/voterpage2.html", {
                "boothID" : boo,
                "booth" : booth,
                "admin" : User.objects.get(pk = booth.admin.id)
            }) 

    return render(request, "wbvs/voterpage1.html", {
        "voterform1" : VoterForm1(),
    })


def access(request, Id):
    Voter.objects.create(boothID = Id, voterID = request.user, allowed = 0, voting_status = "Not Voted")
    return HttpResponseRedirect(reverse("waiting", args=(Id, )))


def waiting(request, Id):
    var = Voter.objects.get(boothID = Id, voterID = request.user)

    allowed = False
    not_allowed = False
    
    if var.allowed == 1:
        allowed = True
    if var.allowed == -1:
        return render(request, "wbvs/homepage.html", {
            "permission_denied" : True
        })
    
    return render(request, "wbvs/waiting.html", {
        "allowed" : allowed,
        "boothID" : Id,
    })


def voterpage3(request , Id):
    if request.method == "POST":
        voter_var = User.objects.get(pk = request.user.id)
        Voter.objects.filter(boothID = Id, voterID = request.user).update(voting_status = "Voted")
        VotingList.objects.create(boothID = Id, candidateID = request.POST["candidate_selected"], voterID = voter_var)
        History.objects.filter(boothID = Id, role = "Voter").update(user = request.user, voting_status = "Voted")
        return render(request, "wbvs/homepage.html", {
            "success_vote" : True
        })
    
    candidate_var = Candidate.objects.filter(boothID = Id).all()
    return render(request, "wbvs/voterpage3.html", {
        "boothId" : Id,
        "candidate_list" : candidate_var
    })


def give_winner(Id):
    entries = Result.objects.filter(boothID = Id).all()
    max = -1
    winner = ""
    for entry in entries:
        if entry.vote_count > max:
            winner = entry.candidateID
            max = entry.vote_count
    
    winner = Candidate.objects.get(candidateID = winner).candidateName
    return winner


def calculate(request, Id):
    Booth.objects.filter(boothID = Id).update(active = False)
    entries = VotingList.objects.filter(boothID = Id).all()
    candidate_list = Candidate.objects.filter(boothID = Id).all()
    for candidate in candidate_list:
        cand_var = Result.objects.create(boothID = Id, candidateID = candidate.candidateID, vote_count = 0)
        count = 0
        for entry in entries:
            if candidate.candidateID == entry.candidateID:
                count += 1
        Result.objects.filter(pk = cand_var.id).update(vote_count = count)
    History.objects.filter(boothID = Id).update(result_declared = True, result = f"{give_winner(Id)} WON", active = False)
    return HttpResponseRedirect(reverse("view_result", args=(Id, )))


def view_result(request, Id):
    booth = Booth.objects.get(boothID = Id)
    result_pg_availaible = not(booth.active)

    entries = Result.objects.filter(boothID = Id).all()
    data = dict()
    for i in entries:
        data[i.candidateID] = i.vote_count

    winner = give_winner(Id)

    return render(request, "wbvs/result.html", {
        "winner" : winner,
        "show_result" : result_pg_availaible,
        "candidates_data" : data,
        "boothID" : Id
    })


def history(request):
    data = History.objects.filter(user = request.user).all()
    return render(request, "wbvs/history.html", {
        "data" : data
    })


def view_details(request):
    return render(request, "wbvs/view_details.html")


def edit_password(request):
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirmation = request.POST["confirmation"]

        if new_password != confirmation:
            return render(request, "wbvs/edit_password.html", {
                "message": "Passwords must match.",
                "passwd_form" : PasswordChangeForm(request.POST)
            })
        User.objects.filter(username = request.user.username).update(password = make_password(new_password))
        return HttpResponseRedirect(reverse("index"))

    return render(request, "wbvs/edit_password.html", {
        "passwd_form" : PasswordChangeForm()
    })