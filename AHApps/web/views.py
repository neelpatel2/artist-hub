from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.conf import settings
from django.core.mail import send_mail
# from .models import ArtistCatalogue, ArtistCatalogueCategory


from functools import wraps

from AHApps.artist.models import Artist, ArtistProfile
from AHApps.master.utils.UNIQUE.generate_otp import create_otp

def login_required(view_func):
    """
    Decorator that requires a user to be authenticated to access the view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('artist_id'):
            messages.error(request, 'You need to login first.')
            return redirect('login_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def register_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']

        new_artist = Artist.objects.create(
            email=email_,
            mobile=mobile_
        )
        new_artist.save()
        messages.success(request, 'Your request has been successfuly submited.')
        return redirect('login_view')
    return render(request, r'web\register.html')

def login_view(request):
    if request.method == 'POST':
        artist_id_ = request.POST['artist_id']
        password_ = request.POST['password']

        try:
            check_artist = Artist.objects.get(artist_id=artist_id_)
            get_artist_profile = ArtistProfile.objects.get(artist_id_id=check_artist.artist_id)

            if not check_artist.is_active:
                messages.warning(request, "Your account is deactive.")
                return redirect('login_view')

        except Artist.DoesNotExist:
            messages.error(request, "Artist ID and password don't match.")
            return redirect('login_view')
        else:
            if check_artist.password == password_:
                request.session['artist_id'] = check_artist.artist_id
                # Store only the URL of the profile image, not the whole object
                request.session['artist_profile_image'] = get_artist_profile.profile.url if get_artist_profile.profile else None
                messages.success(request, "Now, you are logged in.")
                return redirect('dashboard_view')
            else:
                messages.error(request, "Artist ID and password don't match.")
                return redirect('login_view')

    return render(request, 'web/login.html')

@login_required
def logout(request):
    if 'artist_id' in request.session:
        del request.session['artist_id']
        messages.success(request, "Now you are logged out.")
        return redirect('login_view')
    else:
        messages.error(request, 'You are not logged In yet.')
        return redirect('login_view')
    
def forgot_password_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        try:
            check_artist = Artist.objects.get(email=email_)
            if not check_artist.is_active:
                messages.warning(request, "Your account is deactive.")
                return redirect('login_view')
        except Artist.DoesNotExist:
            messages.warning(request, f"{email_} is not exist in our database.")
            return redirect('forgot_password_view')
        else:
            otp_ = create_otp()
            check_artist.otp = otp_
            check_artist.save()
            subject = "Password Reset Request | ARTIST HUB"
            message = f"""
            Dear {check_artist.artist_id},

            We received a request to reset your password. Please use the OTP below to complete the process:

            OTP: {otp_}

            This OTP is valid for a short period of time and will expire soon. If you did not request a password reset, please ignore this email.

            To reset your password, please follow the instructions on our website. If you encounter any issues, contact our support team.

            Best regards,
            The Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [f'{email_}']
        
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Please check your mail.')
            context = {
                'email': email_
            }
            return render(request, 'web\otp-verify.html', context)
    return render(request, r'web\forgot-password.html')
    
def password_reset_request(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']
        new_password_ = request.POST['new_password']
        confirm_password_ = request.POST['confirm_password']

        try:
            check_artist = Artist.objects.get(email=email_)
            if not check_artist.is_active:
                messages.warning(request, "Your account is deactive.")
                return redirect('login_view')
        except Artist.DoesNotExist:
            messages.warning(request, f"{email_} is not exist in our database.")
            return redirect('forgot_password_view')
        else:
            if check_artist.otp == otp_:
                if new_password_ == confirm_password_:
                    check_artist.password = new_password_
                    check_artist.save()
                    messages.success(request, "Password changed successfully.")
                    return redirect('login_view')
                else:
                    messages.error(request, 'new password and confirm password does not match')
                    context = {
                        'email': email_
                    }
                    return render(request, 'web\otp-verify.html', context)
            else:
                messages.error(request, 'Invalid OTP!!!')
                context = {
                    'email': email_
                }
                return render(request, 'web\otp-verify.html', context)
    return render(request, 'web\otp-verify.html')

@login_required
def dashboard_view(request):
    return render(request, r'web\dashboard.html')

@login_required
def catalogue_view(request):
    return render(request, r'web\catalogue.html')

@login_required
def profile_view(request):
    artist_id = request.session['artist_id']
    print(artist_id)
    artist_profile = ArtistProfile.objects.get(artist_id_id=artist_id)
    print(artist_profile)
    context = {
        'profile':artist_profile
    }
    return render(request, r'web\profile.html', context)

@login_required
def forgot_password_profile_view(request):
    artist_id = request.session.get('artist_id')
    
    if artist_id:
        get_pass = Artist.objects.get(artist_id=artist_id)  

        if request.method == 'POST':
            current_password_ = request.POST['current_password']
            new_password_ = request.POST['new_password']
            confirm_password_ = request.POST['confirm_password']

            if current_password_ != get_pass.password:
                messages.error(request, "Current Password is Incorrect")
                return redirect('forgot_password_profile_view')
            elif new_password_ != confirm_password_:
                messages.error(request, "New Password and Confirm Password do not match")
                return redirect('forgot_password_profile_view')
            elif current_password_ == new_password_:
                messages.error(request, "Current Password and New Password cannot be the same")
                return redirect('forgot_password_profile_view')
            
            get_pass.password = new_password_
            get_pass.save()
            messages.success(request, "Password updated successfully")
            return redirect('profile_view')  
        return render(request, 'web/forgot_password_profile.html')
    else:
        messages.error(request, "Session expired. Please login again.")
        return redirect('login_view')
    
@login_required
def add_catalogue_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        categories = request.POST.getlist('categories') 
        catalogue_image = request.FILES.get('catalogue_image')

        if title and content and categories and catalogue_image:
            catalogue = ArtistCatalogue(
                title=title,
                content=content,
                catalogue_image=catalogue_image
            )
            catalogue.save()

            category_objects = ArtistCatalogueCategory.objects.filter(id__in=categories)
            catalogue.categories.set(category_objects)

            messages.success(request, 'Catalogue added successfully.')
            return redirect('catalogue_list')  
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'web/catalogue.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        mobile_ = request.POST.get('mobile')
        first_name_ = request.POST.get('first_name')
        last_name_ = request.POST.get('last_name')
        gender_ = request.POST.get('gender')
        address_=request.POST.get('address')

        artist_id_ = request.session['artist_id']
        artist = Artist.objects.get(artist_id=artist_id_)
        artist_profile = ArtistProfile.objects.get(artist_id_id=artist_id_)

        # Only update the profile image if a new file is uploaded
        if 'profile' in request.FILES:
            profile_ = request.FILES['profile']
            artist_profile.profile = profile_  # Update with new file
        # Else, keep the existing profile image unchanged

        # Update the other fields
        artist_profile.first_name = first_name_
        artist_profile.last_name = last_name_
        artist_profile.gender = gender_
        artist_profile.address=address_
        artist.mobile = mobile_

        artist.save()
        artist_profile.save()

        # Update the session with the new profile image URL if updated
        if artist_profile.profile:
            request.session['artist_profile_image'] = artist_profile.profile.url

        messages.success(request, 'Profile data updated successfully.')
        return redirect('profile_view')
    
    # In case of GET requests or other methods, handle accordingly
    return render(request, 'profile_update.html')

@csrf_exempt
@login_required
def update_date_of_birth(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        date_of_birth = data.get('date_of_birth')

        if date_of_birth:
            artist_id_ = request.session['artist_id']
            profile, created = ArtistProfile.objects.get_or_create(artist_id_id=artist_id_)
            profile.date_of_birth = parse_date(date_of_birth)
            profile.save()
            return JsonResponse({'success': True})
        
    return JsonResponse({'success': False}, status=400)



