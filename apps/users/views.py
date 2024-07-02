from competitions.models import Module
from django.utils.html import strip_tags
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import message, send_mail, BadHeaderError
from django.http import HttpResponse
from django.views import View
from .utils import token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from .forms import UserRegisterForm, UserUpdateForm, UserLoginForm
from django.core.mail import send_mail
from .models import NewUser
from django.urls import reverse
from django.conf import settings
import requests
import secrets
from django.contrib.sites.models import Site





User = get_user_model()

########### register here #####################################

def registeration_success(request):
    return render(request,'authentication/registeration_success.html') 

def registeration_failure(request):
    return render(request,'authentication/registeration_failure.html')

    







from django.db import transaction

@transaction.atomic
def register(request):
    # print(domain)
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            unique_username = form.cleaned_data['username']
            if request.POST.get('referred_by'):
                alcherid = request.POST.get('referred_by')
                requests.put('https://ambassador.alcheringa.in/api/referal_id/', data={'alcherid': alcherid, 'points': 50})

            user = form.save(commit=False)
            user.username = unique_username
            user.save()
            memberid = create_new_ref_number()
            member=TeamMembers(memberid = memberid, name=user.fullname,email=user.email,phone=user.phone_number,gender=user.gender)
            member.save()
            team = Team(name="undefined", leader=user)
            team.members.add(member)
            team.save()
            send_email_verification(request, user)
            messages.success(request, 'Please check your email to complete the registration.')
            return redirect('login')
                   
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')

    else:
        form = UserRegisterForm()

    return render(request, 'authentication/register.html', {'form': form, 'title': 'Register Here', 'active_page': 'signup'})


def send_email_verification(request, user):
    subject = 'Activate Your Account'
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = Site.objects.get_current()

    domain = request.META['HTTP_HOST']
    link = reverse('verify_email', kwargs={
                    'uidb64': uidb64, 'token': token_generator.make_token(user)})
    message = render_to_string('authentication/email_verify_mail copy.txt', {
        'user': user,
        "link": 'https://'+domain+link,
    })
    user_email=user.email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [
                user_email], fail_silently=False)

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
       
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'authentication/registeration_success.html')
        else:
            return render(request, 'authentication/registeration_failure.html')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'authentication/registeration_failure.html')

################ login forms###################################################

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')
        print(password)
        user = NewUser.objects.filter(email=email).first()
        if user:
            if user.is_active == False:
                messages.error(request, "Account not verified")
               
            else:
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    auth_login(request, user)
                    return redirect(request.GET.get('next', 'home'))
                else:
                    print("errrr")
                    messages.error(
                        request, 'Password is incorrect for the email address entered ')
        else:
            print("email not registered")
            messages.error(request, 'Email is not registered')

    return render(request, 'authentication/login.html', {'title': 'log in','active_page':"Login"})








def password_reset_request(request):
    User = get_user_model()
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(
                Q(email=data, provider="email"))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "authentication/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Alcheringa Web Operations',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.EMAIL_HOST_USER, [
                                  user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(
                        request, ("Password reset mail sent successfully."))
                    return redirect('password_reset_done')    
            else:
                messages.error(request, ("Email not registered with us"))
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="authentication/password/password_reset.html", context={"password_reset_form": password_reset_form})

def password_reset_done(request):
    return render(request,'authentication/password/password_reset_done.html')




@login_required(login_url='login')
def profile(request):
    modules = Module.objects.all()
    if request.method == 'POST':
        u_form = UserUpdateForm(
            request.POST, request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your Profile has been updated!')
            return redirect('profile')
        print(u_form.errors)
    else:
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'authentication/profile.html', {'heading': 'Profile', 'form': u_form, 'modules': modules, 'totalmodules': modules.count(),'active_page':'profile'})


@login_required(login_url='login')
def profileedit(request):
    modules = Module.objects.all()
    if request.method == 'POST':
        u_form = UserUpdateForm(
            request.POST, request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your Profile has been updated!')
            return redirect('profile')
        print(u_form.errors)
    else:
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'authentication/profile_edit.html', {'heading': 'Profile', 'form': u_form, 'modules': modules, 'totalmodules': modules.count(),'active_page':'profile'})


def logout(request):
    django_logout(request)
    return redirect('home')


class VerificationView(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = NewUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, NewUser.DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('home')
        else:
            messages.warning(
                request, ('The confirmation link was invalid, possibly because it has already been used.'))
            print("err")
            return redirect('home')

def data_registered_users(request):
    users=NewUser.objects.all()
    if request.user.is_staff:
        return render(request,'authentication/registered_users.html',{'users':users})
    
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import MemberForm
from .models import TeamMembers, Team
from competitions.models import Competition
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string

# Create your views here.

# @login_required(login_url='login')
# def team_members(request,pk=0):
#     team = Team.objects.filter(leader=request.user).first()
#     all_members = []
#     mincheck=False
#     if pk!='0':
#         comp = Competition.objects.get(id=pk)
#         team_members = team.members.all().count()
#         mincheck=comp.min_members<=team_members

#     for member in team.members.all():
#         all_members.append(member)
#     return render(request, 'teams/team_members.html', {'team': all_members,'active_page':'team','pk':pk,'mincheck':mincheck})


def create_new_ref_number():
    memberid = "MEM-"
    memberid += str(TeamMembers.objects.count()+5001)+"-"
    memberid += get_random_string(length=4)
    if TeamMembers.objects.filter(memberid=memberid).exists():
        return create_new_ref_number()
    return memberid


@login_required(login_url='login')
def add_member(request,pk):
    memberemail = TeamMembers.objects.filter(
        email=request.POST.get('addemail'))
    if request.method == 'POST':
        if (memberemail.count() > 0):
            return HttpResponse('User with same email already exist')
        
        memberid = create_new_ref_number()
        # if(request.FILES.getlist('addimg')):
        #     TeamMembers(memberid = memberid, img=request.FILES.getlist('addimg')[0], name=request.POST.get('addname'),
        #             email=request.POST.get('addemail'), phone=request.POST.get('addphone'), gender=request.POST.get('addgender')).save()
        # else:
        TeamMembers(memberid = memberid, name=request.POST.get('addname'),
                    email=request.POST.get('addemail'), phone=request.POST.get('addphone'), gender=request.POST.get('addgender')).save()
            
        team = Team.objects.get(leader=request.user)
        team.members.add(TeamMembers.objects.get(
            email=request.POST.get('addemail')))
        team.save()
        if pk!='0':
            comp = Competition.objects.get(id=pk)
            team_members = team.members.all().count()
            if(team_members<comp.min_members):
                if(comp.min_members-team_members==1):
                    messages.info(request,"Add atleast " +str(comp.min_members-team_members)+ " more member to register for "+ comp.event_name)
                else:
                    messages.info(request,"Add atleast " +str(comp.min_members-team_members)+ " more members to register for "+ comp.event_name)
    return redirect('TeamMembers')


@login_required(login_url='login')
def update_member(request):
    memberemail = TeamMembers.objects.filter(email=request.POST.get('editemail'))
    member = TeamMembers.objects.get(id=request.POST.get('editid'))
    if request.method == 'POST':
        if (memberemail.count() > 0 and member not in memberemail):
            return HttpResponse('User with same email already exist')

        if(request.FILES.getlist('editimg')):
            member.img = request.FILES.getlist('editimg')[0]
        member.name = request.POST.get('editname')
        member.email = request.POST.get('editemail')
        member.phone = request.POST.get('editphone')
        member.gender = request.POST.get('editgender')
        member.save()
    return HttpResponse('OK')


@login_required(login_url='login')
def remove_member(request):
    if request.POST["id"]:
        member = TeamMembers.objects.filter(id=request.POST["id"]).first()
        team=Team.objects.get(leader=request.user)
        team.members.remove(member)
        team.save()
        member.delete()
        return HttpResponse("ok")

