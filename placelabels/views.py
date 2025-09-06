from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateObjForm, CreatePlaceForm, CreateObjTypeForm, CreateBoxForm, RoomForm
from .models import Objects, PlaceLabel, ObjType, BoxLabel, Room
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# -------------------
# Crear habitación AJAX
# -------------------
@csrf_exempt
def create_room_ajax(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Debes iniciar sesión.'})

        data = json.loads(request.body)
        name = data.get('name','').strip()

        if not name:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})

        if Room.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe una habitación con ese nombre'})

        room = Room.objects.create(user=request.user, name=name)
        return JsonResponse({'success': True, 'id': room.id, 'name': room.name})
    return JsonResponse({'success': False, 'error': 'Método inválido'})


# -------------------
# Crear cajón AJAX
# -------------------
@csrf_exempt
def create_box_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        place_id = data.get('place')
        name = data.get('name','').strip()

        if not place_id:
            return JsonResponse({'success': False, 'error': 'Debes seleccionar un lugar'})

        try:
            place = PlaceLabel.objects.get(pk=place_id)
        except PlaceLabel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lugar no válido'})

        box = BoxLabel.objects.create(place=place, name=name or place.name, user=place.user)
        return JsonResponse({'success': True, 'id': box.id, 'name': box.name})
    return JsonResponse({'success': False, 'error': 'Método inválido'})


@csrf_exempt
def create_place_ajax(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Debes iniciar sesión.'})

        data = json.loads(request.body)
        name = data.get('name','').strip()
        desc = data.get('description','').strip()
        room_id = data.get('room_id')

        if not name:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        if not room_id:
            return JsonResponse({'success': False, 'error': 'Debes seleccionar una habitación'})

        try:
            room = Room.objects.get(user=request.user, id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Habitación inválida'})

        if PlaceLabel.objects.filter(user=request.user, name=name, room=room).exists():
            return JsonResponse({'success': False, 'error': 'Ese lugar ya existe en esta habitación.'})

        place = PlaceLabel.objects.create(user=request.user, name=name, description=desc, room=room)
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

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': None  # No necesitamos el UserCreationForm
        })

    # POST
    us_name = request.POST.get('username', '').strip()
    pass1 = request.POST.get('password1', '')
    pass2 = request.POST.get('password2', '')

    if pass1 != pass2:
        return render(request, 'signup.html', {
            'error': 'Las contraseñas no coinciden 😅',
            'username': us_name
        })

    try:
        user = User.objects.create_user(username=us_name, password=pass1)
        user.save()
        login(request, user)
        return redirect('objects')
    except IntegrityError:
        return render(request, 'signup.html', {
            'error': 'Ese usuario ya existe 😬',
            'username': us_name
        })


# CREATE
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.user = request.user  # <-- asignar el usuario
            room.save()
            return redirect('rooms')
    else:
        form = RoomForm()
    return render(request, 'create_room.html', {'form': form})

        
def create_obj(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    if request.method == 'GET':
        form = CreateObjForm(user=user)
        error = None
    else: 
        form = CreateObjForm(request.POST, user=user)
        if form.is_valid():
            new_obj = form.save(commit=False)
            new_obj.user = user
            new_obj.save()
            return redirect('objects')
        else:
            error = 'Por favor completa los datos correctamente'

    # Traer habitaciones y lugares del usuario
    user_rooms = Room.objects.filter(user=user).order_by('name')
    user_places = PlaceLabel.objects.filter(user=user).order_by('name')

    return render(request, 'create_obj.html', {
        'form': form,
        'error': error,
        'user_rooms': user_rooms,
        'user_places': user_places
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
            return redirect('places')
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
            return redirect('objtypes')
        else:
            return render(request, 'create_objtype.html', {
                'form': form,
                'error': 'Por favor completa los datos correctamente'
            })
        
def create_box(request):
    if request.method == "POST":
        form = CreateBoxForm(request.POST, user=request.user)
        if form.is_valid():
            box = form.save(commit=False)
            box.user = request.user
            # Generar name/pseudonym si es necesario
            count = BoxLabel.objects.filter(user=request.user, place=box.place).count() + 1
            box.name = f"{box.place.pseudonym}-C{count}"
            box.save()
            return redirect("boxes")
    else:
        form = CreateBoxForm(user=request.user)

    return render(request, "create_box.html", {"form": form})


        
def objects(request):
    rooms = Room.objects.all()                # para mostrar habitaciones
    places = PlaceLabel.objects.all()        # para mostrar lugares/muebles
    boxes = BoxLabel.objects.all()           # para mostrar cajones
    objtypes = ObjType.objects.all()         # para mostrar tipos de objeto

    query = request.GET.get('q', '')         # término de búsqueda
    room_id = request.GET.get('room')        # filtro por habitación
    place_id = request.GET.get('place')      # filtro por placelabel
    box_id = request.GET.get('box')          # filtro por cajón
    type_id = request.GET.get('type')        # filtro por tipo de objeto

    objs = Objects.objects.filter(user=request.user)

    # Filtrar por habitación
    if room_id:
        objs = objs.filter(
            Q(placelabel__room_id=room_id) |
            Q(boxlabel__place__room_id=room_id)
        )

    # Filtrar por lugar/mueble
    if place_id:
        objs = objs.filter(placelabel_id=place_id)

    # Filtrar por cajón
    if box_id:
        objs = objs.filter(boxlabel_id=box_id)

    # Filtrar por tipo de objeto
    if type_id:
        objs = objs.filter(label_id=type_id)

    # Filtrar por búsqueda
    if query:
        objs = objs.filter(
            Q(name__icontains=query) |
            Q(placelabel__room__name__icontains=query) |
            Q(placelabel__pseudonym__icontains=query) |
            Q(boxlabel__pseudonym__icontains=query) |
            Q(boxlabel__place__room__name__icontains=query)
        ).distinct()

    return render(request, 'objects.html', {
        'objs': objs,
        'rooms': rooms,
        'places': places,
        'boxes': boxes,
        'objtypes': objtypes,
        'query': query,
        'selected_room': room_id,
        'selected_place': place_id,
        'selected_box': box_id,
        'selected_type': type_id
    })

def places(request):
    places = PlaceLabel.objects.filter(user=request.user)
    return render(request, 'places.html', {'places': places})

def objtypes(request):
    objtypes = ObjType.objects.filter(user=request.user)
    return render(request, 'objtypes.html', {'objtypes': objtypes})

def object_detail(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)
    return render(request, 'object_detail.html', {'obj': obj})

def boxes(request):
    boxes = BoxLabel.objects.filter(user=request.user)
    return render(request, 'boxes.html', {'boxes': boxes})

def rooms(request):
    user_rooms = Room.objects.filter(user=request.user)
    return render(request, 'rooms.html', {'rooms': user_rooms})



# UPDATE

def edit_object(request, pk):
    obj = get_object_or_404(Objects, pk=pk, user=request.user)

    # Traemos lugares y habitaciones del usuario para los modales
    user_places = PlaceLabel.objects.filter(user=request.user)
    user_rooms = Room.objects.filter(user=request.user)

    if request.method == 'GET':
        form = CreateObjForm(instance=obj, user=request.user)
        return render(request, 'edit_object.html', {
            'form': form,
            'obj': obj,
            'user_places': user_places,
            'user_rooms': user_rooms
        })
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
                'user_places': user_places,
                'user_rooms': user_rooms,
                'error': 'Por favor completa los datos correctamente'
            })


def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk) 
    if request.method == 'GET':
        form = RoomForm(instance=room)
        return render(request, 'edit_room.html', {'form': form, 'obj': room})
    else:  # POST
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('rooms')
        else:
            return render(request, 'edit_room.html', {
                'form': form,
                'obj': room,
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

def edit_box(request, pk):
    box = get_object_or_404(BoxLabel, pk=pk, user=request.user)

    if request.method == 'GET':
        form = CreateBoxForm(instance=box)
        return render(request, 'edit_box.html', {'form': form, 'obj': box})
    else:  # POST
        form = CreateBoxForm(request.POST, instance=box)
        if form.is_valid():
            edited_box = form.save(commit=False)
            edited_box.user = request.user  
            edited_box.save()
            return redirect('boxes')
        else:
            return render(request, 'edit_box.html', {
                'form': form,
                'obj': box,
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
    return redirect("places") 

def delete_objtype(request, pk):
    objtype = get_object_or_404(ObjType, pk=pk)
    objtype.delete()
    return redirect("objtypes")  
def delete_box(request, pk):
    box = get_object_or_404(BoxLabel, pk=pk)
    box.delete()
    return redirect("boxes")
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.delete()
    return redirect("rooms")


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
