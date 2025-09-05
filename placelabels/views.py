from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateObjForm, CreatePlaceForm, CreateObjTypeForm
from .models import Objects, PlaceLabel, ObjType
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_place_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name').strip()
        desc = data.get('description','').strip()
        if PlaceLabel.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({'success': False, 'error': 'Ese lugar ya existe.'})
        place = PlaceLabel.objects.create(user=request.user, name=name, description=desc)
        return JsonResponse({'success': True, 'id': place.id, 'name': place.name})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

@csrf_exempt
def create_objtype_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        typename = data.get('typename').strip()
        if ObjType.objects.filter(user=request.user, typename=typename).exists():
            return JsonResponse({'success': False, 'error': 'Ese tipo de objeto ya existe.'})
        objtype = ObjType.objects.create(user=request.user, typename=typename)
        return JsonResponse({'success': True, 'id': objtype.id, 'name': objtype.typename})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
    })
    else:
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        us_name = request.POST['username']

        if pass1 == pass2 :
            try:
                user = User.objects.create_user(username=us_name, password=pass1)
                user.save()
                login(request, user)
                return redirect('objects')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Ya existe el usuario wey xd'
                })
        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Buzo padrino, las contraseñas no coinciden xd'
                })


# CREATE
def create_obj(request):
    if request.method == 'GET':
        form = CreateObjForm(user=request.user)
        return render(request, 'create_obj.html', {'form': form})
    else: 
        form = CreateObjForm(request.POST, user=request.user)
        if form.is_valid():
            new_obj = form.save(commit=False)
            new_obj.user = request.user
            new_obj.save()
            return redirect('objects')
        else:
            return render(request, 'create_obj.html', {
                'form': form,
                'error': 'Por favor completa los datos correctamente'
            })

        
def create_place(request):
    if request.method == 'GET':
        form = CreatePlaceForm()
        return render(request, 'create_place.html', {'form': form})
    else:  # POST
        form = CreatePlaceForm(request.POST)
        if form.is_valid():
            new_place = form.save(commit=False)
            new_place.user = request.user
            new_place.save()
            return redirect('objects')
        else:
            return render(request, 'create_place.html', {
                'form': form,
                'error': 'Por favor completa los datos correctamente'
            })

def create_objtype(request):
    if request.method == 'GET':
        form = CreateObjTypeForm()
        return render(request, 'create_objtype.html', {'form': form})
    else:  # POST
        form = CreateObjTypeForm(request.POST)
        if form.is_valid():
            new_objtype = form.save(commit=False)
            new_objtype.user = request.user
            new_objtype.save()
            return redirect('objects')
        else:
            return render(request, 'create_objtype.html', {
                'form': form,
                'error': 'Por favor completa los datos correctamente'
            })
        
# READ
def objects(request):
    objs = Objects.objects.filter(user=request.user)
    return render(request, 'objects.html', {'objs': objs})

def places(request):
    places = PlaceLabel.objects.filter(user=request.user)
    return render(request, 'places.html', {'places': places})

def objtypes(request):
    objtypes = ObjType.objects.filter(user=request.user)
    return render(request, 'objtypes.html', {'objtypes': objtypes})

def object_detail(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)
    return render(request, 'object_detail.html', {'obj': obj})

# UPDATE
def edit_object(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreateObjForm(instance=obj, user=request.user)
        return render(request, 'edit_object.html', {'form': form, 'obj': obj})
    else:  # POST
        form = CreateObjForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            edited_obj = form.save(commit=False)
            edited_obj.user = request.user  
            edited_obj.save()
            return redirect('objects')
        else:
            return render(request, 'edit_object.html', {
                'form': form,
                'obj': obj,
                'error': 'Por favor completa los datos correctamente'
            })
        
def edit_object(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreateObjForm(instance=obj, user=request.user)
        return render(request, 'edit_object.html', {'form': form, 'obj': obj})
    else:  # POST
        form = CreateObjForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            edited_obj = form.save(commit=False)
            edited_obj.user = request.user  
            edited_obj.save()
            return redirect('objects')
        else:
            return render(request, 'edit_object.html', {
                'form': form,
                'obj': obj,
                'error': 'Por favor completa los datos correctamente'
            })


def edit_object(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreateObjForm(instance=obj, user=request.user)
        return render(request, 'edit_object.html', {'form': form, 'obj': obj})
    else:  # POST
        form = CreateObjForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            edited_obj = form.save(commit=False)
            edited_obj.user = request.user  
            edited_obj.save()
            return redirect('objects')
        else:
            return render(request, 'edit_object.html', {
                'form': form,
                'obj': obj,
                'error': 'Por favor completa los datos correctamente'
            })


def edit_objtype(request, pk):
    objtype = get_object_or_404(ObjType, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreateObjTypeForm(instance=objtype)
        return render(request, 'edit_objtype.html', {'form': form, 'obj': objtype})
    else:  # POST
        form = CreateObjTypeForm(request.POST, instance=objtype)
        if form.is_valid():
            edited_obj = form.save(commit=False)
            edited_obj.user = request.user  
            edited_obj.save()
            return redirect('objtypes')
        else:
            return render(request, 'edit_objtype.html', {
                'form': form,
                'obj': objtype,
                'error': 'Por favor completa los datos correctamente'
            })


def edit_place(request, pk):
    place = get_object_or_404(PlaceLabel, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreatePlaceForm(instance=place)
        return render(request, 'edit_place.html', {'form': form, 'obj': place})
    else:  # POST
        form = CreatePlaceForm(request.POST, instance=place)
        if form.is_valid():
            edited_place = form.save(commit=False)
            edited_place.user = request.user  
            edited_place.save()
            return redirect('places')
        else:
            return render(request, 'edit_place.html', {
                'form': form,
                'obj': place,
                'error': 'Por favor completa los datos correctamente'
            })
# DELETE
def delete_object(request, pk):
    obj = get_object_or_404(Objects, pk=pk)
    obj.delete()
    return redirect("objects")  

def delete_place(request, pk):
    place = get_object_or_404(PlaceLabel, pk=pk)
    place.delete()
    return redirect("objects") 

def delete_objtype(request, pk):
    objtype = get_object_or_404(ObjType, pk=pk)
    objtype.delete()
    return redirect("objects")  



def mylogout(request):
    logout(request)
    return redirect('home')

def mylogin(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {
            'form': AuthenticationForm,
            'error': 'Nombre o contraseña incorrectos... truchas'
            })
        else:
            login(request, user)
            return redirect('objects')
