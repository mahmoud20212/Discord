from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *

def index(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/index.html', context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body'),
        )
        room.participants.add(request.user)
        return HttpResponseRedirect(reverse('room_detail', args=[room.id]))
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_room(request):
    topics = Topic.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('index')
    context = {
        'form': form,
        'topics': topics,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    topics = Topic.objects.all()
    room = Room.objects.get(pk=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponseForbidden()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('index')

    context = {
        'form': form,
        'topics': topics,
        'room': room,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(pk=pk)

    if request.user != room.host:
        return HttpResponseForbidden()

    if request.method == 'POST':
        room.delete()
        return redirect('index')
    context = {
        'obj': room,
    }
    return render(request, 'base/delete.html', context)

def user_login(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user != None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Username OR password does not exist')
    context = {
        'page': page,
    }
    return render(request, 'user/login.html', context)

def user_register(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'An error occured during registration')
    context = {
        'page': page,
        'form': form,
    }
    return render(request, 'user/login.html', context)

@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
    }
    return render(request, 'user/profile.html', context)

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(pk=pk)

    if request.user != message.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        message.delete()
        return HttpResponseRedirect(reverse('room_detail', args=[str(message.room.id)]))
    
    context = {
        'obj': message,
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user-profile', args=[user.id]))
    context = {
        'form': form,
    }
    return render(request, 'user/update_user.html', context)

def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q) 
    context = {
        'topics': topics,
    }
    return render(request, 'base/topics.html', context)

def activity_page(request):
    room_messages = Message.objects.all()
    context = {
        'room_messages': room_messages,
    }
    return render(request, 'base/activity.html', context)