from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from WandrLog.models import Traveler, Destination


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address')

    class Meta:
        model = Traveler
        fields = ("email", "password1", "password2", "first_name", "last_name", "zip_code", "city", "address", "phone", "bio")


class TravelerAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Traveler
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login")


class TravelerUpdateForm(forms.ModelForm):
    class Meta:
        model = Traveler
        fields = ("email", "first_name", "last_name", "city", "address", "phone", "bio")#, "is_admin", "is_active", "is_superuser", "is_staff" )

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                traveler = Traveler.objects.exclude(pk=self.instance.pk).get(email=email)
            except Traveler.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s" is already in use.' % email)


class DestinationUpdateForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ("city_name", "latitude", "longitude", "country_code")


class UserForm(forms.Form):
    first_name = forms.CharField(label='first_name', max_length=100)
    last_name = forms.CharField(label='last_name', max_length=100)
    city_id = forms.IntegerField(label='city id')
    city = forms.CharField(label='city', max_length=100)
    zip_code = forms.CharField(label='zip_code', max_length=5)
    email = forms.CharField(label='email', max_length=100)
    phone = forms.CharField(label='phone', max_length=100)
    address = forms.CharField(label='address', max_length=200)


class TripForm(forms.Form):
    trip_name = forms.CharField(label='Trip Title', max_length=100)
    trip_description = forms.CharField(label='Trip Description', max_length=100)
    destination_id = forms.IntegerField(label='destination_id', widget=forms.HiddenInput())
    destination_name = forms.CharField(label='Destination')
    cover_image = forms.ImageField(label='cover_image')


class VisitForm(forms.Form):
    visit_name = forms.CharField(label='name', max_length=100)
    visit_place = forms.CharField(label='place', max_length=100)
    visit_att_id = forms.IntegerField(label='visit_att_id', widget=forms.HiddenInput())
    visit_log = forms.CharField(label='log', max_length=100)
    visit_image = forms.ImageField(label='image')


class CommentForm(forms.Form):
    traveler_id = forms.IntegerField(label='traveler_id')
    comment = forms.CharField(label='comment', max_length=100)


