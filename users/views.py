import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout, \
    update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.service import paginate_queryset
from users.constants import AUTOCOMPLETE_LIMIT
from users.forms import LoginForm, PasswordChangeForm, ProfileEditForm, \
    RegistrationForm
from users.models import Skill, User


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """Регистрация нового пользователя"""
    form = RegistrationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:project_list')

    return render(request, 'users/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Авторизация пользователя"""
    form = LoginForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('projects:project_list')

        form.add_error(None, 'Неверный имейл или пароль')

    return render(request, 'users/login.html', {'form': form})


@require_http_methods(['GET'])
def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    return redirect('projects:project_list')


@require_http_methods(['GET'])
def profile_view(request, user_id):
    """Публичный профиль пользователя"""
    profile_user = get_object_or_404(User, id=user_id)

    context = {
        'user': profile_user,
        'is_owner': request.user == profile_user,
    }

    return render(request, 'users/user-details.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def edit_profile_view(request):
    """Редактирование профиля пользователя"""
    form = ProfileEditForm(request.POST or None,
                            request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('users:profile', user_id=request.user.id)

    return render(request, 'users/edit_profile.html', {'form': form})


@require_http_methods(['GET'])
def users_list_view(request):
    """Список всех пользователей с фильтрацией по навыкам"""
    users_list = User.objects.all().order_by('-id')
    all_skills = Skill.objects.all().order_by('name')
    active_skill = request.GET.get('skill', '')

    if active_skill:
        users_list = users_list.filter(skills__name=active_skill)

    page_obj, query_prefix = paginate_queryset(users_list, request)

    context = {
        'participants': page_obj,
        'page_obj': page_obj,
        'all_skills': [skill.name for skill in all_skills],
        'all_skills_objects': all_skills,
        'active_skill': active_skill,
        'query_prefix': query_prefix,
    }

    return render(request, 'users/participants.html', context)


@require_http_methods(['GET'])
def skill_autocomplete(request):
    """Автодополнение для навыков"""
    q = request.GET.get('q', '')

    if q:
        skills = Skill.objects.filter(
            name__istartswith=q).order_by('name')[:AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.all().order_by('name')[:AUTOCOMPLETE_LIMIT]

    skills_data = [
        {'id': skill.id, 'name': skill.name}
        for skill in skills
    ]

    return JsonResponse(skills_data, safe=False)


@require_http_methods(['POST'])
@login_required
def add_skill_view(request, user_id):
    """Добавление навыка пользователю"""
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'У вас нет прав на изменение этого профиля'},
            status=HTTPStatus.FORBIDDEN
        )

    user = request.user

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'},
                            status=HTTPStatus.BAD_REQUEST)

    skill_id = data.get('skill_id')
    skill_name = data.get('name')

    created = False
    added = False
    skill = None

    if skill_id:
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return JsonResponse({'error': 'Навык не найден'},
                                status=HTTPStatus.NOT_FOUND)

    elif skill_name:
        skill_name = skill_name.strip()
        skill, created = Skill.objects.get_or_create(name=skill_name)

    else:
        text = 'Не передан skill_id или name'
        return JsonResponse({'error': text}, status=HTTPStatus.BAD_REQUEST)

    if skill and not user.skills.filter(id=skill.id).exists():
        user.skills.add(skill)
        added = True

    return JsonResponse({
        'id': skill.id if skill else None,
        'name': skill.name if skill else None,
        'created': created,
        'added': added
    })


@require_http_methods(['POST'])
@login_required
def remove_skill_view(request, user_id, skill_id):
    """Удаление навыка у пользователя"""
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'У вас нет прав на изменение этого профиля'},
            status=HTTPStatus.FORBIDDEN
        )

    user = request.user

    try:
        skill = Skill.objects.get(id=skill_id)
    except Skill.DoesNotExist:
        return JsonResponse({'error': 'Навык не найден'},
                            status=HTTPStatus.NOT_FOUND)

    if not user.skills.filter(id=skill.id).exists():
        text = 'У пользователя нет этого навыка'
        return JsonResponse({'error': text}, status=HTTPStatus.BAD_REQUEST)

    user.skills.remove(skill)

    if skill.users.count() == 0:
        skill.delete()

    return JsonResponse({'removed': True})


@require_http_methods(['GET', 'POST'])
@login_required
def change_password_view(request):
    """Смена пароля пользователя"""
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('users:profile', user_id=request.user.id)

    return render(request, 'users/change_password.html', {'form': form})
