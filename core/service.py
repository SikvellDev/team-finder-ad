from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest

from projects.constants import OBJECTS_NUMBER_ON_PAGE


def paginate_queryset(queryset,
                      request: HttpRequest,
                      per_page: int = OBJECTS_NUMBER_ON_PAGE):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += '&'

    return page_obj, query_prefix
