from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db import connection, transaction

from .forms import RegistrationForm, TravelerAuthenticationForm, TravelerUpdateForm, TripForm, UserForm, VisitForm, DestinationUpdateForm
from .models import Traveler, Destination, Friend, Favorites

import pymongo
from collections import namedtuple
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

def psqlRawCmdRet(cmd):
    cursor = connection.cursor()
    cursor.execute(cmd)
    return cursor.fetchall()


'''---------------- Views ---------------------- '''
def index(request):
    favorite_rank = psqlRawCmdRet("SELECT * FROM favorite_rank LIMIT 10")
    favorite_rank = [{'name': x[0], 'count': x[1]} for x in favorite_rank]
    return render(request,'WandrLog/index.html', {'favorite_rank': favorite_rank})

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
    db = getMongoClient()
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE id = %s;', [traveler_id])[0]
    context['traveler'] = traveler


    context['trips'] = db.Trips.find({'traveler_id': traveler.id})
    friends = psqlRawCmdRet('SELECT * FROM friend WHERE (traveller_id = {} OR friend_id = {})'.format(traveler_id, traveler_id))
    context['friend_count'] = len(friends)
    results = psqlRawCmdRet('SELECT * FROM friend WHERE (traveller_id = {} AND friend_id = {}) OR (traveller_id = {} AND friend_id = {});'.format(traveler_id, request.user.id, request.user.id, traveler_id))
    context['friends'] = results
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
        form = UserForm(initial={'first_name': traveler.first_name, 'last_name': traveler.last_name, 'city':traveler.city, 'city_id': traveler.city_id, 'email': traveler.email, 'phone':traveler.phone, 'address':traveler.address})
        return render(request, 'WandrLog/account/edit.html', {'form':form, 'traveler':traveler})

def friend(request, traveler_id):
    cmd = "INSERT INTO Friend(traveller_id, friend_id, date_of_friendship) VALUES ("+ str(request.user.id) + ", " + str(traveler_id) + ", CAST (\'" + str(datetime.datetime.utcnow().date())+ "\'AS DATE));"
    psqlRawCommand(cmd)
    return redirect('account', traveler_id=traveler_id)

def unfriend(request, traveler_id):
    cmd = "DELETE FROM Friend WHERE (traveller_id = {} AND friend_id = {}) OR (traveller_id = {} AND friend_id = {});".format(traveler_id, request.user.id, request.user.id, traveler_id)
    psqlRawCommand(cmd)
    return redirect('account', traveler_id=traveler_id)

def statistics(request):
    return render(request,'WandrLog/statistics.html')

def statistics_chart(request):
    labels = []
    data = []
    favorite_rank = psqlRawCmdRet("SELECT * FROM favorite_rank LIMIT 20")
    for x in favorite_rank:
        labels.append(x[0])
        data.append(x[1])
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    }) 

def total_miles_traveled_by_user_chart(request):
    labels = []
    data = []
    distance_traveled = psqlRawCmdRet("select * from traveler_distance_traveled;")
    for x in distance_traveled:
        labels.append(str(x[1]) + ' ' + str(x[2]))
        data.append(x[3])
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    }) 

def zipcode_form(request):
    query = request.GET.get('q')
    zipcodes = psqlRawCmdRet('SELECT zip_code, city_name FROM zipcodes WHERE zip_code LIKE \'{}%\' LIMIT 10;'.format(query))
    print(zipcodes)
    zipcodes = [{'zip_code':x[0], 'city_name':x[1]} for x in zipcodes]
    html = render_to_string(
            template_name='WandrLog/_partials/_zipcodes_form.html', 
            context={'zipcodes': zipcodes}
        )
    return JsonResponse(data={"html_from_view": html}, safe=False)
    


def attractions(request):
    if not request.user.is_authenticated:
        return redirect("login")

    query = request.GET.get('q')

    if request.is_ajax():
        if query == None:
            attractions = psqlRawCmdRet('SELECT * FROM attractions LIMIT 1000;')
        else:
            attractions = psqlRawCmdRet('SELECT * FROM attractions WHERE name LIKE \'{}\';'.format('%'+ query + '%'))
        html = render_to_string(
                template_name='WandrLog/_partials/_attractions.html', 
                context={'attractions': attractions}
            )
        return JsonResponse(data={"html_from_view": html}, safe=False)
    else:

        attractions = psqlRawCmdRet('SELECT * FROM attractions LIMIT 1000;')
        return render(request, 'WandrLog/attractions.html', {'attractions': attractions})

def attractions_form(request, trip_id):
    query = request.GET.get('q')
    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
    destination = Destination.objects.raw('SELECT * FROM destination WHERE id = {};'.format(trip['destination_id']))[0]
    print(query)
    print(destination.city_name)
    attractions = psqlRawCmdRet('SELECT * FROM attractions WHERE (name LIKE \'{}\') AND distance(latitude, longitude, {}, {})<50 LIMIT 100;'.format('%' + query + '%', destination.latitude, destination.longitude))
    attractions = [{'id':x[0], 'name':x[1], 'zip':x[3]} for x in attractions]
    print(attractions)
    html = render_to_string(
            template_name='WandrLog/_partials/_attractions_results_form.html', 
            context={'attractions': attractions}
        )
    return JsonResponse(data={"html_from_view": html}, safe=False)


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
            #destination = Destination.objects.raw('SELECT * FROM destination WHERE city_name=%s;', [form.cleaned_data.get('destination_name')])[0]

            trip = {
                'trip_name': form.cleaned_data.get('trip_name'),
                'trip_description': form.cleaned_data.get('trip_description'),
                'traveler_id': request.user.id,
                'destination_id': form.cleaned_data.get('destination_id'), 
                'destination_name': form.cleaned_data.get('destination_name'),
                'cover_image':  base64.encodebytes(data.read()).decode('utf-8') ,
                'visits':[],
                'comments':[],
                'likes': [],
                'published': datetime.datetime.utcnow()
            }
            db.Trips.insert_one(trip).inserted_id

            return redirect('trips')
    else:

        form = TripForm()
        context ['trip_form'] = form
        return render(request, 'WandrLog/trips/create_trip.html', context)
# 
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
                                                                       'destination_id' : form.cleaned_data.get('destination_id'),
                                                                       'trip_description': form.cleaned_data.get('trip_description'),
                                                                       'destination_name': form.cleaned_data.get('destination_name'),
                                                                       'cover_image':  base64.encodebytes(data.read()).decode('utf-8')}})

            return redirect('trips')
    else:
        print()
        form = TripForm(initial= {"trip_name": trip["trip_name"],
                                 "destination_id": trip["destination_id"],
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
    locations = []
    i = len(trip['visits'])
    for visit in trip['visits']:
        if visit['visit_id'] != -1: 
            viz = psqlRawCmdRet("SELECT * FROM attractions WHERE id = {} AND name = \'{}\';".format(visit['visit_place_id'], visit['visit_place']))[0]
            locations.append({'name':viz[1], 'lat': viz[6], 'long':viz[7], 'idx': i})
        i-=1
    print(locations)
    traveler = Traveler.objects.raw('SELECT * FROM traveler WHERE id = %s;', [trip['traveler_id']])[0]
    destination = Destination.objects.raw('SELECT * FROM destination WHERE id=%s;', [trip['destination_id']])[0]
    return render(request,'WandrLog/trips/view_trip.html', {'trip': trip, 'traveler': traveler, 'destination': destination, 'locations':locations})

#---------------- Visit Views -------------------
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
                'visit_place_id': form.cleaned_data.get('visit_att_id'),
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

# Comments & Likes for Trips
def create_comment(request, trip_id):
    if not request.user.is_authenticated:
        return redirect("login")
 
    comment = request.GET.get('c')
    if comment:
        client = pymongo.MongoClient('mongodb://root:password@mongodb:27017/')
        db = client['trips']
        trip = db.Trips.find_one({'_id':ObjectId(trip_id)})

        comment = { 'comment_id': len(trip['comments']),
                    'user_id': request.user.id,
                    'user_name': request.user.first_name + ' ' + request.user.last_name,
                    'comment': comment,
                    'published': datetime.datetime.utcnow()
                   }

        if trip['comments'] is None:
            trip['comments'] = [comment]
        else:
            trip['comments'].append(comment) 

        db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "comments": trip['comments']}})

    return redirect('view_trip', trip_id=trip_id)


def delete_comment(request, trip_id, comment_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    db = getMongoClient()
    trip = db.Trips.find_one({'_id':ObjectId(trip_id)})
    comment = trip['comments'][int(comment_id)]

    if comment['comment_id'] == -1:
        return redirect('view_trip', trip_id=trip_id)

    comment['comment_id'] = -1 #emptied as to not disturb index 
    comment['user_id'] = ''
    comment['user_name'] = ''
    comment['comment'] = ''
    comment['published'] = ''


    db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "comments": trip['comments'] }})

    return redirect('view_trip', trip_id=trip_id)

def like(request, trip_id):
    if request.is_ajax():
        db = getMongoClient()
        trip = db.Trips.find_one({'_id':ObjectId(trip_id)})

        if trip['likes'] is None:
            trip['likes'] = [request.user.id]
        else:
            if request.user.id in trip['likes']:
                trip['likes'].remove(request.user.id)
            else:
                trip['likes'].append(request.user.id)

        db.Trips.update_one({'_id':ObjectId(trip_id)}, { "$set": { "likes": trip['likes'] }})

        context= {}
        context['like_count'] = len(trip['likes'])
        return JsonResponse(context)
    else:
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
    favorites = psqlRawCmdRet('SELECT * FROM favorites WHERE traveller_id = {}'.format(request.user.id))
    favorites = [x[1] for x in favorites]
    print(favorites)
    if not request.is_ajax():


        if query:
            destination = Destination.objects.filter(name__icontains=query)
        else:
            destination = Destination.objects.raw('SELECT * FROM destination WHERE id < 1000;')
            
        return render(request, 'WandrLog/destinations/destinations.html', {'destination': destination, 'favorites': favorites})
    else:
        caller = request.META.get('HTTP_REFERER')
       
        if 'create_trip' in caller or 'edit_trip' in caller:
            destination = psqlRawCmdRet('SELECT id, city_name, state FROM destination_states_d WHERE (city_name LIKE \'{}\') LIMIT 10;'.format('%' + query + '%'))
            destination = [{'id':x[0], 'city_name':x[1], 'state':x[2]} for x in destination]
            html = render_to_string(
                template_name='WandrLog/_partials/_destination_results_form.html', 
                context={'destination': destination, 'favorites':favorites}
            )
        
        else:
            destination = Destination.objects.raw('SELECT * FROM destination_states_zip WHERE city_name LIKE %s;', [query + '%'])
            html = render_to_string(
                template_name='WandrLog/_partials/_destination_results.html', 
                context={'destination': destination, 'favorites': favorites}
            )
        return JsonResponse(data={"html_from_view": html}, safe=False)
        

def destinations_signup(request):
    query = request.GET.get('q')


    destination = Destination.objects.raw('SELECT * FROM destination WHERE city_name LIKE %s LIMIT 10;', [query + '%'])
    html = render_to_string(
                template_name='WandrLog/_partials/_destination_results_form.html', 
                context={'destination': destination}
            )
        
    return JsonResponse(data={"html_from_view": html}, safe=False)

def favorite(request, destination_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")

    cmd = "INSERT INTO Favorites(traveller_id, dest_id) VALUES ("+ str(request.user.id) + ", " + str(destination_id) + " );"
    psqlRawCommand(cmd)
    return redirect('destinations')

def unfavorite(request, destination_id):
    context = {}

    if not request.user.is_authenticated:
        return redirect("login")
        
    cmd = "DELETE FROM Favorites WHERE traveller_id="+ str(request.user.id) + "AND dest_id=" + str(destination_id) + ";"
    psqlRawCommand(cmd)
    return redirect('destinations')

