from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from projects.constants import CLOSED_PROJECT, OPEN_PROJECT
from projects.forms import ProjectForm
from projects.models import Project
from service import paginate_queryset


@require_http_methods(['GET'])
def project_list_view(request):
    """View для отображения списка всех проектов"""
    projects_list = Project.objects.all(
    ).order_by('-created_at').prefetch_related('participants')

    page_obj, query_prefix = paginate_queryset(projects_list, request)

    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'query_prefix': query_prefix,
    }

    return render(request, 'projects/project_list.html', context)


@require_http_methods(['GET'])
def project_detail_view(request, project_id):
    """Страница детального просмотра проекта"""
    project = get_object_or_404(Project, id=project_id)

    context = {
        'project': project,
    }

    return render(request, 'projects/project-details.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def project_create_view(request):
    """Создание нового проекта"""
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()

        project.participants.add(request.user)

        return redirect('projects:project_detail', project_id=project.id)

    context = {
        'form': form,
        'is_edit': False,
        'title': 'Создание проекта',
    }

    return render(request, 'projects/create-project.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def project_edit_view(request, project_id):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return redirect('projects:project_detail', project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('projects:project_detail', project_id=project.id)

    context = {
        'form': form,
        'is_edit': True,
        'title': 'Редактирование проекта',
        'project': project,
    }

    return render(request, 'projects/create-project.html', context)


@login_required
@require_http_methods(['POST'])
def complete_project_view(request, project_id):
    """Завершение проекта (меняет статус на closed)"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        text = 'Вы не являетесь автором этого проекта'
        return JsonResponse(
            {'status': 'error', 'message': text},
            status=HTTPStatus.FORBIDDEN
        )

    if project.status != OPEN_PROJECT:
        return JsonResponse(
            {'status': 'error', 'message': 'Проект уже завершён'},
            status=HTTPStatus.BAD_REQUEST
        )

    project.status = CLOSED_PROJECT
    project.save()

    return JsonResponse({
        'status': 'ok',
        'project_status': CLOSED_PROJECT
    })


@login_required
@require_http_methods(["POST"])
def toggle_participate_view(request, project_id):
    """Добавление или удаление пользователя из участников проекта"""

    project = get_object_or_404(Project, id=project_id)

    if project.owner == request.user:
        return JsonResponse(
            {
                "status": "error",
                "message": "Вы не можете участвовать в своём проекте"
            },
            status=HTTPStatus.BAD_REQUEST
        )

    is_participating = project.participants.filter(
        id=request.user.id
    ).exists()

    if is_participating:
        project.participants.remove(request.user)

        return JsonResponse({
            "status": "ok",
            "participating": False,
            "button_text": "Участвовать",
            "participants_count": project.participants.count(),
        })

    project.participants.add(request.user)

    return JsonResponse({
        "status": "ok",
        "participant": True,
        "button_text": "Отказаться от участия",
        "participants_count": project.participants.count(),
    })
