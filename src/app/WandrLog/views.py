from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db import connection, transaction

from .forms import RegistrationForm, TravelerAuthenticationForm, TravelerUpdateForm, TripForm, UserForm, VisitForm, DestinationUpdateForm
from .models import Traveler, Destination

import pymongo
from bson.objectid import ObjectId

import base64
import datetime

MONGO_USER = 'root'
MONGO_PASS = 'password'
MONGO_HOST = 'mongodb:27017'
MONGO_NAME = 'trips'

'''------------ Helper Functions --------------- '''
def getMongoClient():
    client = pymongo.MongoClient('mongodb://root:password@mongodb:27017/')
    db = client['trips']
    return db

def psqlRawCommand(cmd):
    cursor = connection.cursor()
    cursor.execute(cmd)


'''---------------- Views ---------------------- '''
def index(request):
    return render(request,'WandrLog/index.html')

#---------------- User Views -------------------
def sign_up(request):
    context = {}

    if request.user.is_authenticated:
        return redirect("home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user =  authenticate(email=email, password=raw_password)
            login(request, user)
            return render(request,'WandrLog/index.html')
    context['form']=form
    return render(request,'WandrLog/account/sign_up.html',context)

def log_in(request):
    context = {}

    if request.user.is_authenticated:
        return redirect("home")

    if request.POST:
        form = TravelerAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email,password=password)

            if user:
                login(request, user)
                return redirect("home")

    else:
        form = TravelerAuthenticationForm()
        
    context['login_form'] = form
    return render(request, 'WandrLog/account/login.html', context)

def log_out(request):
    if not request.user.is_authenticated:
        return redirect("login")
        
    logout(request)
    return redirect('home')

def traveler_profile(request, traveler_id):

    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE id = %s;', [traveler_id])[0]
    context['traveler'] = traveler

    db = getMongoClient()
    context['trips'] = db.Trips.find({'traveler_id':traveler.id})
    return render(request, 'WandrLog/account/account.html', context)

def traveler_update(request, traveler_id):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    if request.POST:
        form = TravelerUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            #data = request.FILES['profile_picture']
            #form.cleaned_data['profile_picture'] = base64.encodebytes(data.read()).decode('utf-8')
            form.save()
            return redirect('account', traveler_id=traveler_id)
    else:
        form = TravelerUpdateForm(
            initial = {
                "email": request.user.email,
                "first_name": request.user.first_name, 
                "last_name": request.user.last_name, 
                "address": request.user.address, 
                "phone": request.user.phone, 
                "bio": request.user.bio
            }
        )
    context ['account_form'] = form
    context ['traveler_id'] = traveler_id
    return render(request, 'WandrLog/account/account_edit.html', context)

def users(request):
    if not request.user.is_authenticated:
        return redirect("login")

    query = request.GET.get('q')
    if not query:
        traveler = Traveler.objects.all
    else:
        traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE first_name = %s;', [query])
    return render(request, 'WandrLog/account/users.html', {'traveler': traveler})

def delete_user(request, traveler_id):
    if not request.user.is_authenticated:
        return redirect("login")

    psqlRawCommand('DELETE FROM traveler WHERE id = {};'.format(traveler_id))
    db = getMongoClient()
    db.Trips.delete({'traveler_id':traveler_id})

    return redirect('/WandrLog/users')

def edit(request, traveler_id):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            for key in form.cleaned_data:
                psqlRawCommand('UPDATE traveler SET ' + str(key) + ' = \'' + str(form.cleaned_data[key]) + '\' WHERE id= ' + str(traveler_id) + ';')
            return redirect('/WandrLog/users')
    else:
        traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE id = %s;', [traveler_id])[0]
        form = UserForm(initial={'first_name': traveler.first_name, 'last_name': traveler.last_name, 'email': traveler.email, 'phone':traveler.phone, 'address':traveler.address})
        return render(request, 'WandrLog/account/edit.html', {'form':form, 'traveler':traveler})

#---------------- Trip Views -------------------
def create_trip(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    if request.POST:
        form = TripForm(request.POST, request.FILES)
        if form.is_valid():
            db = getMongoClient()
            data = request.FILES['cover_image']
            destination = Destination.objects.raw('SELECT * FROM destination WHERE city_name=%s;', [form.cleaned_data.get('destination_name')])[0]

            trip = {
                'trip_name': form.cleaned_data.get('trip_name'),
                'trip_description': form.cleaned_data.get('trip_description'),
                'traveler_id': request.user.id,
                'destination_id': destination.id, 
                'destination_name': destination.city_name,
                'cover_image':  base64.encodebytes(data.read()).decode('utf-8') ,
                'visits':[],
                'comments':[],
                'published': datetime.datetime.utcnow()
            }
            db.Trips.insert_one(trip).inserted_id

            return redirect('trips')
    else:

        form = TripForm()
        context ['trip_form'] = form
        return render(request, 'WandrLog/trips/create_trip.html', context)

def create_visit(request, trip_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")
    
    db = getMongoClient()

    if request.POST:
        form = VisitForm(request.POST, request.FILES)
        if form.is_valid():

            trip = db.Trips.find_one({'_id':ObjectId(trip_id)})

            data = request.FILES['visit_image']

            if trip['visits'] != None and trip['visits'] != [] :
                vid = trip['visits'][-1]['visit_id'] + 1
            else:
                vid = 0

            visit = {
                'visit_id': vid,
                'visit_name': form.cleaned_data.get('visit_name'),
                'visit_place': form.cleaned_data.get('visit_place'),
                'visit_log': form.cleaned_data.get('visit_log'),
                'visit_image':  base64.encodebytes(data.read()).decode('utf-8') ,
                'published': datetime.datetime.utcnow()
            }

            if trip['visits'] != None:
                trip['visits'].append(visit)
            else:
                trip['visits'] = [visit]

            db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "visits": trip['visits'] }})

            return redirect('view_trip', trip_id=trip_id)
    else:
        form = VisitForm()
        context ['visit_form'] = form
        context ['trip'] = db.Trips.find_one({'_id':ObjectId(trip_id)})
    return render(request, 'WandrLog/trips/create_visit.html', context)

def edit_visit(request, trip_id, visit_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
    visit = trip['visits'][int(visit_id)]


    if visit == {'visit_id': -1}:
        return redirect('view_trip', trip_id=trip_id)
        
    if request.POST:
        form = VisitForm(request.POST, request.FILES)
        if form.is_valid():

            data = request.FILES['visit_image']

            visit['visit_name'] = form.cleaned_data.get('visit_name')
            visit['visit_place'] = form.cleaned_data.get('visit_place')
            visit['visit_log'] = form.cleaned_data.get('visit_log')
            visit['visit_image'] = base64.encodebytes(data.read()).decode('utf-8')

            db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "visits": trip['visits'] }})

            return redirect('view_trip', trip_id=trip_id)
    else:
        form = VisitForm(initial =
                                {'visit_name':  visit['visit_name'], 
                                'visit_place':  visit['visit_place'],
                                'visit_log':  visit['visit_log'],
                                'visit_image':  visit['visit_image']
                                }
                                )
        context ['visit_form'] = form
        context ['trip'] = db.Trips.find_one({'_id':ObjectId(trip_id)})
        context ['visit_id'] = visit_id
    return render(request, 'WandrLog/trips/edit_visit.html', context)
        
def delete_visit(request, trip_id, visit_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
    visit = trip['visits'][int(visit_id)]

    if visit == {'visit_id': -1}:
        return redirect('view_trip', trip_id=trip_id)

    visit['visit_id'] = -1 #emptied as to not disturb index 
    visit['visit_name'] = ''
    visit['visit_place'] = ''
    visit['visit_log'] = ''
    visit['visit_image'] = ''
    
    db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "visits": trip['visits'] }})

    return redirect('view_trip', trip_id=trip_id)

def edit_trip(request, trip_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})

    if request.POST:
        form = TripForm(request.POST, request.FILES)
        if form.is_valid():

            data = request.FILES['cover_image']

            db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "trip_name": form.cleaned_data.get('trip_name'),
                                                                       'trip_description': form.cleaned_data.get('trip_description'),
                                                                       'destination_name': form.cleaned_data.get('destination_name'),
                                                                       'cover_image':  base64.encodebytes(data.read()).decode('utf-8')}})

            return redirect('trips')
    else:
        form = TripForm(initial= {"trip_name": trip["trip_name"],
                                 "trip_description": trip["trip_description"], 
                                "destination_name": trip["destination_name"]})
        context ['trip_form'] = form
        context ['trip_id'] = trip_id
    return render(request, 'WandrLog/trips/edit_trip.html', context)

def delete_trip(request, trip_id):
    if not request.user.is_authenticated:
        return redirect("login")
    db = getMongoClient()
    db.Trips.delete_one({'_id':ObjectId(trip_id)})
    return redirect('/WandrLog/trips')

def trips(request):
    db = getMongoClient()
    return render(request,'WandrLog/trips/trips.html', {'trips': db.Trips.find({})})

def view_trip(request, trip_id):
    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
    traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE id = %s;', [trip['traveler_id']])[0]
    destination = Destination.objects.raw('SELECT * FROM destination WHERE id=%s;', [trip['destination_id']])[0]
    return render(request,'WandrLog/trips/view_trip.html', {'trip': trip, 'traveler': traveler, 'destination': destination})

def create_comment(request, trip_id):
    if not request.user.is_authenticated:
        return redirect("login")

    comment = request.GET.get('c')
    if comment:
        client = pymongo.MongoClient('mongodb://root:password@mongodb:27017/')
        db = client['trips']
        trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
        comment = {'user_id': request.user.id,
                   'user_name': request.user.first_name + ' ' + request.user.last_name,
                   'comment': comment,
                    'published': datetime.datetime.utcnow()
                   }

        if trip['comments'] is None:
            trip['comments'] = [comment]
        else:
            trip['comments'].insert(0, comment) 

        db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "comments": trip['comments']}})

    return redirect('view_trip', trip_id=trip_id)

#---------------- Destinations Views -------------------
def destination_delete(request, destination_id):
    psqlRawCommand('DELETE FROM destination WHERE id = {};'.format(destination_id))
    return redirect('/WandrLog/destinations')


def destination_update(request, destination_id):

    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    if request.POST:
        form = DestinationUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            for key in form.cleaned_data:
                psqlRawCommand('UPDATE destination SET ' + str(key) + ' = \'' + str(form.cleaned_data[key]) + '\' WHERE id= ' + str(destination_id) + ';')

            return redirect('destinations')
    else:
        destination = Destination.objects.raw('SELECT * FROM destination WHERE id=%s;', [destination_id])[0]
        form = DestinationUpdateForm(
            initial = {
                "city_name": destination.city_name,
                "latitude": destination.latitude,
                "longitude": destination.longitude,
                "country_code": destination.country_code
            }
        )
    context ['destination_form'] = form
    context['destination'] = destination
    return render(request, 'WandrLog/destinations/destination_update.html', context)


def destinations(request):
    query = request.GET.get('q')
    if not request.is_ajax():
        if query:
            destination = Destination.objects.filter(name__icontains=query)
        else:
            destination = Destination.objects.raw('SELECT * FROM destination WHERE id < 1000;')
        return render(request, 'WandrLog/destinations/destinations.html', {'destination': destination})
    else:
        caller = request.META.get('HTTP_REFERER')
       
        if 'create_trip' in caller or 'edit_trip' in caller:
            destination = Destination.objects.raw('SELECT * FROM destination WHERE city_name LIKE %s LIMIT 10;', [query + '%'])
            html = render_to_string(
                template_name='WandrLog/_partials/_destination_results_form.html', 
                context={'destination': destination}
            )
        
        else:
            destination = Destination.objects.raw('SELECT * FROM destination WHERE city_name LIKE %s;', [query + '%'])
            html = render_to_string(
                template_name='WandrLog/_partials/_destination_results.html', 
                context={'destination': destination}
            )
        return JsonResponse(data={"html_from_view": html}, safe=False)
        


