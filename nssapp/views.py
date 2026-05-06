from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserTab, BloodBank, PledgeCertificate, Event, Notification
from .decorators import login_required_custom, role_required_custom
from django.db.models import Q
from datetime import date, datetime

# --- PUBLIC VIEWS ---

def home(request):
    return render(request, 'home.html')

def bloodbank_list(request):
    query = request.GET.get('q')
    if query:
        donors = BloodBank.objects.filter(
            Q(regno__icontains=query) |
            Q(name__icontains=query) |
            Q(blood_group__icontains=query)
        )
    else:
        donors = BloodBank.objects.all()
    return render(request, 'bloodbank_list.html', {'donors': donors, 'query': query})

def register(request):
    if request.method == 'POST':
        regno = request.POST.get('regno')
        name = request.POST.get('name')
        department = request.POST.get('department')
        year = request.POST.get('year')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        if UserTab.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, 'register.html')

        # New registration: Default to volunteer and pending
        # Plain text password storage
        user = UserTab(
            regno=regno,
            name=name,
            department=department,
            year=year,
            phone=phone,
            email=email,
            password=password,
            role='volunteer',
            join_date=date.today(),
            address=address,
            status='pending'
        )
        user.save()
        messages.success(request, "Registration successful. Wait for NSS Leader approval.")
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not role:
            messages.error(request, "Please select role")
            return render(request, 'login.html')

        try:
            # Validate login using email + role
            user = UserTab.objects.get(email=email, role=role)
            
            # Plain text password validation
            if password == user.password:
                # Approval check ONLY for volunteers
                if user.role == 'volunteer' and user.status == 'pending':
                    messages.warning(request, "Your account is pending approval. Please wait for NSS Leader approval.")
                    return render(request, 'login.html')
                
                # Set session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role

                # Redirect based on role
                if user.role == 'volunteer':
                    return redirect('volunteer_dashboard')
                elif user.role == 'nssleader':
                    return redirect('leader_dashboard')
                elif user.role == 'admin':
                    return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid credentials")
        except UserTab.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('home')


# --- VOLUNTEER MODULE ---

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_dashboard(request):
    user = UserTab.objects.get(id=request.session['user_id'])
    upcoming_events = Event.objects.all().order_by('-event_date')[:5]
    notifications = Notification.objects.filter(Q(target_role='volunteer') | Q(target_role='all')).order_by('-created_at')[:5]
    return render(request, 'volunteer_dashboard.html', {
        'user': user,
        'upcoming_events': upcoming_events,
        'notifications': notifications
    })

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_profile(request):
    user = UserTab.objects.get(id=request.session['user_id'])
    return render(request, 'volunteer_profile.html', {'user': user})

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def edit_profile(request):
    user = UserTab.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.department = request.POST.get('department')
        user.year = request.POST.get('year')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('volunteer_dashboard')
    return render(request, 'edit_profile.html', {'user': user})

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = UserTab.objects.get(id=request.session['user_id'])
        
        if old_password != user.password:
            messages.error(request, "Incorrect old password!")
            return render(request, 'change_password.html')
            
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match!")
            return render(request, 'change_password.html')
            
        user.password = new_password
        user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('volunteer_dashboard')
        
    return render(request, 'change_password.html')

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_bloodbank_register(request):
    if request.method == 'POST':
        regno = request.POST.get('regno')
        name = request.POST.get('name')
        age = request.POST.get('age')
        blood_group = request.POST.get('blood_group')
        phone = request.POST.get('phone')

        if BloodBank.objects.filter(regno=regno).exists():
            messages.error(request, "You have already registered in Blood Bank.")
            return render(request, 'bloodbank_register.html')
            
        if BloodBank.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return render(request, 'bloodbank_register.html')

        donor = BloodBank(
            regno=regno,
            name=name,
            age=age,
            blood_group=blood_group,
            phone=phone
        )
        donor.save()
        messages.success(request, "Blood Donor Registered Successfully")
        return redirect('bloodbank_list')

    return render(request, 'bloodbank_register.html')


@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_pledge(request):
    user_id = request.session['user_id']
    if PledgeCertificate.objects.filter(user_id=user_id).exists():
        messages.info(request, "You have already taken the pledge.")
        return redirect('volunteer_certificates')

    if request.method == 'POST':
        user = UserTab.objects.get(id=user_id)
        pledge_text = "I pledge that I will never use drugs, alcohol, or any harmful substances. I will live a healthy and responsible life and inspire others to stay drug free."
        
        pledge = PledgeCertificate(
            user_id=user_id,
            name=user.name,
            role='volunteer',
            pledge_text=pledge_text,
            pledge_date=date.today(),
            certificate_code=f"CERT2026{user_id}"
        )
        pledge.save()
        messages.success(request, "Pledge Taken Successfully! Your certificate is generated.")
        return redirect('volunteer_certificates')

    return render(request, 'pledge.html')

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_certificates(request):
    user_id = request.session['user_id']
    certificates = PledgeCertificate.objects.filter(user_id=user_id)
    return render(request, 'certificates.html', {'certificates': certificates})

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_events(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'volunteer_events.html', {'events': events})

@login_required_custom
@role_required_custom(allowed_roles=['volunteer'])
def volunteer_notifications(request):
    notifications = Notification.objects.filter(Q(target_role='volunteer') | Q(target_role='all')).order_by('-created_at')
    return render(request, 'volunteer_notifications.html', {'notifications': notifications})


# --- NSS LEADER MODULE ---

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_dashboard(request):
    pending_count = UserTab.objects.filter(status='pending', role='volunteer').count()
    approved_count = UserTab.objects.filter(status='approved', role='volunteer').count()
    notifications = Notification.objects.filter(Q(target_role='nssleader') | Q(target_role='all')).order_by('-created_at')[:5]
    return render(request, 'leader_dashboard.html', {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'notifications': notifications
    })

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def schedule_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        place = request.POST.get('place')
        
        # Get day from date
        dt = datetime.strptime(event_date, '%Y-%m-%d')
        event_day = dt.strftime('%A')
        
        event = Event(
            title=title,
            description=description,
            event_date=event_date,
            event_day=event_day,
            event_time=event_time,
            place=place,
            created_by_id=request.session['user_id']
        )
        event.save()
        messages.success(request, "Event Scheduled Successfully")
        return redirect('leader_dashboard')
        
    return render(request, 'schedule_event.html')

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_send_notification(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        notif = Notification(
            title=title,
            message=message,
            sender_role='nssleader',
            sender_id_id=request.session['user_id'],
            target_role='volunteer'
        )
        notif.save()
        messages.success(request, "Notification sent to all volunteers.")
        return redirect('leader_dashboard')
        
    return render(request, 'leader_send_notification.html')

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_notifications(request):
    notifications = Notification.objects.filter(Q(target_role='nssleader') | Q(target_role='all')).order_by('-created_at')
    return render(request, 'leader_notifications.html', {'notifications': notifications})

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def pending_volunteers(request):
    volunteers = UserTab.objects.filter(status='pending', role='volunteer')
    return render(request, 'pending_volunteers.html', {'volunteers': volunteers})

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def approve_volunteer(request, user_id):
    user = get_object_or_404(UserTab, id=user_id)
    user.status = 'approved'
    user.save()
    messages.success(request, "Volunteer Approved Successfully")
    return redirect('pending_volunteers')

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def reject_volunteer(request, user_id):
    user = get_object_or_404(UserTab, id=user_id)
    user.delete()
    messages.warning(request, "Volunteer Registration Rejected and Deleted")
    return redirect('pending_volunteers')

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def approved_volunteers(request):
    volunteers = UserTab.objects.filter(status='approved', role='volunteer')
    return render(request, 'approved_volunteers.html', {'volunteers': volunteers})

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_view_volunteer_profile(request, id):
    # Fetch volunteer by id and ensure role is 'volunteer'
    volunteer = get_object_or_404(UserTab, id=id, role='volunteer')
    return render(request, 'leader_view_volunteer_profile.html', {'v': volunteer})

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_bloodbank_register(request):
    if request.method == 'POST':
        regno = request.POST.get('regno')
        name = request.POST.get('name')
        age = request.POST.get('age')
        blood_group = request.POST.get('blood_group')
        phone = request.POST.get('phone')

        if BloodBank.objects.filter(regno=regno).exists():
            messages.error(request, "You have already registered in Blood Bank.")
            return render(request, 'bloodbank_register.html')
            
        if BloodBank.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return render(request, 'bloodbank_register.html')

        donor = BloodBank(
            regno=regno,
            name=name,
            age=age,
            blood_group=blood_group,
            phone=phone
        )
        donor.save()
        messages.success(request, "Blood Donor Registered Successfully")
        return redirect('bloodbank_list')

    return render(request, 'bloodbank_register.html')


@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_pledge(request):
    user_id = request.session['user_id']
    if PledgeCertificate.objects.filter(user_id=user_id).exists():
        messages.info(request, "You have already taken the pledge.")
        return redirect('leader_certificates')

    if request.method == 'POST':
        user = UserTab.objects.get(id=user_id)
        pledge_text = "I pledge that I will never use drugs, alcohol, or any harmful substances. I will live a healthy and responsible life and inspire others to stay drug free."
        
        pledge = PledgeCertificate(
            user_id=user_id,
            name=user.name,
            role='nssleader',
            pledge_text=pledge_text,
            pledge_date=date.today(),
            certificate_code=f"CERT2026{user_id}"
        )
        pledge.save()
        messages.success(request, "Pledge Taken Successfully! Your certificate is generated.")
        return redirect('leader_certificates')

    return render(request, 'pledge.html')

@login_required_custom
@role_required_custom(allowed_roles=['nssleader'])
def leader_certificates(request):
    user_id = request.session['user_id']
    certificates = PledgeCertificate.objects.filter(user_id=user_id)
    return render(request, 'certificates.html', {'certificates': certificates})


# --- ADMIN MODULE ---

@login_required_custom
@role_required_custom(allowed_roles=['admin'])
def admin_dashboard(request):
    total_volunteers = UserTab.objects.filter(role='volunteer').count()
    total_leaders = UserTab.objects.filter(role='nssleader').count()
    total_pending = UserTab.objects.filter(status='pending').count()
    return render(request, 'admin_dashboard.html', {
        'total_volunteers': total_volunteers,
        'total_leaders': total_leaders,
        'total_pending': total_pending
    })

@login_required_custom
@role_required_custom(allowed_roles=['admin'])
def volunteer_list(request):
    volunteers = UserTab.objects.filter(role='volunteer', status='approved')
    return render(request, 'volunteer_list.html', {'volunteers': volunteers})

@login_required_custom
@role_required_custom(allowed_roles=['admin'])
def nssleader_list(request):
    leaders = UserTab.objects.filter(role='nssleader')
    return render(request, 'nssleader_list.html', {'leaders': leaders})

@login_required_custom
@role_required_custom(allowed_roles=['admin'])
def admin_send_notification(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        target_role = request.POST.get('target_role') # volunteer, nssleader, all
        
        notif = Notification(
            title=title,
            message=message,
            sender_role='admin',
            sender_id_id=request.session['user_id'],
            target_role=target_role
        )
        notif.save()
        messages.success(request, f"Notification sent to {target_role}.")
        return redirect('admin_dashboard')
        
    return render(request, 'admin_send_notification.html')

@login_required_custom
@role_required_custom(allowed_roles=['admin'])
def make_leader(request, id):
    volunteer = get_object_or_404(UserTab, id=id, role='volunteer')
    volunteer.role = 'nssleader'
    volunteer.status = 'approved'
    volunteer.save()
    
    # Send notification to the user
    notif = Notification(
        title="Promotion Notice",
        message="You are promoted as NSS Leader by Admin.",
        sender_role='admin',
        sender_id_id=request.session['user_id'],
        target_role='nssleader' # They are now a leader
    )
    notif.save()
    
    messages.success(request, f"{volunteer.name} has been promoted to NSS Leader.")
    return redirect('volunteer_list')

@login_required_custom
def view_certificate(request, id):
    certificate = get_object_or_404(PledgeCertificate, id=id)
    
    # Security check: User can only view their own certificate
    if certificate.user_id != request.session['user_id']:
        messages.error(request, "Unauthorized access to certificate.")
        role = request.session.get('user_role')
        if role == 'volunteer':
            return redirect('volunteer_dashboard')
        elif role == 'nssleader':
            return redirect('leader_dashboard')
        return redirect('home')
        
    return render(request, 'certificate_view.html', {'cert': certificate})
