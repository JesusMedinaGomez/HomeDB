from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateObjForm, CreatePlaceForm, CreateObjTypeForm, CreateBoxForm, RoomForm, ObjectsFormSet
from .models import Objects, PlaceLabel, ObjType, BoxLabel, Room
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

def get_places_by_room(request, room_id):
    places = PlaceLabel.objects.filter(room_id=room_id, user=request.user)
    data = [{"id": p.id, "name": p.name} for p in places]
    return JsonResponse(data, safe=False)

def get_boxes_by_place(request, place_id):
    boxes = BoxLabel.objects.filter(place_id=place_id, user=request.user)
    data = [{"id": b.id, "name": b.name} for b in boxes]
    return JsonResponse(data, safe=False)

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

def create_objects_bulk(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        formset = ObjectsFormSet(request.POST, queryset=Objects.objects.none(), form_kwargs={'user': user})
        if formset.is_valid():
            objs = formset.save(commit=False)
            for obj in objs:
                obj.user = user
                obj.save()
            return redirect('objects')
    else:
        formset = ObjectsFormSet(queryset=Objects.objects.none(), form_kwargs={'user': user})

    return render(request, 'create_objects_bulk.html', {'formset': formset})

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
    user_rooms = Room.objects.filter(user=request.user)
    user_places = PlaceLabel.objects.filter(user=request.user)
    user_boxes = BoxLabel.objects.filter(user=request.user)
    user_types = ObjType.objects.filter(user=request.user)

    if request.method == "POST":
        # Obtenemos los objetos enviados por JS
        objects_json = request.POST.get('objects_data')
        if not objects_json:
            return render(request, 'create_obj.html', {
                'error': "Agrega al menos un objeto antes de guardar",
                'user_rooms': user_rooms,
                'user_places': user_places,
                'user_boxes': user_boxes,
                'user_types': user_types,
            })

        objects_list = json.loads(objects_json)

        for obj_data in objects_list:
            obj = Objects(
                name=obj_data.get('name'),
                description=obj_data.get('description'),
                important=obj_data.get('important', False),
                whoIsIt=obj_data.get('whoIsIt') or "Yo",
                hasIt=obj_data.get('hasIt') or "Yo",
                isInPlace=obj_data.get('isInPlace', True),
                user=request.user
            )

            # Campos compartidos
            placelabel_id = obj_data.get('placelabel')
            boxlabel_id = obj_data.get('boxlabel')
            type_id = obj_data.get('type')

            if placelabel_id:
                try:
                    obj.placelabel = PlaceLabel.objects.get(id=placelabel_id, user=request.user)
                except:
                    pass
            if boxlabel_id:
                try:
                    obj.boxlabel = BoxLabel.objects.get(id=boxlabel_id, user=request.user)
                except:
                    pass
            if type_id:
                try:
                    obj.label = ObjType.objects.get(id=type_id, user=request.user)
                except:
                    pass

            obj.save()

        # Redirigir a la lista de objetos
        return redirect('objects')

    # ----->>> aquí capturas los GET params
    preselected = {
        "room": request.GET.get("room"),
        "place": request.GET.get("place"),
        "box": request.GET.get("box"),
    }

    # Si es GET, renderizamos el formulario vacío
    return render(request, 'create_obj.html', {
        'user_rooms': user_rooms,
        'user_places': user_places,
        'user_boxes': user_boxes,
        'user_types': user_types,
        'preselected': preselected,   # <-- agregado
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

    # Traemos lugares, habitaciones y tipos del usuario para los modales
    user_places = PlaceLabel.objects.filter(user=request.user)
    user_rooms = Room.objects.filter(user=request.user)
    user_types = ObjType.objects.filter(user=request.user)  # <-- agregar esto

    if request.method == 'GET':
        form = CreateObjForm(instance=obj, user=request.user)
        return render(request, 'edit_object.html', {
            'form': form,
            'obj': obj,
            'user_places': user_places,
            'user_rooms': user_rooms,
            'user_types': user_types,  # <-- agregar al contexto
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
                'user_types': user_types,  # <-- agregar al contexto
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
