from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from rest_framework.filters import BaseFilterBackend

from lizard_security.models import UserGroup
from ddsc_site.models import Visibility

DEFAULT_CREATOR_FIELD = 'creator'
DEFAULT_VISIBILITY_FIELD = 'visibility'

class WorkspaceCollageFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        '''
        Returns a subset of the model instances, filtered on visibility.

        When filtering needs to occur on related models, declare 'filter_field_prefix'
        on your view.

        Public workspaces are always visible, private Workspace only to their creator,
        and "usergroups" workspace only to all people in the same user groups.
        '''
        filter_field_prefix = view.filter_field_prefix if hasattr(view, 'filter_field_prefix') else ''
        return filter_objects_for_user(view.model, request.user, queryset, filter_field_prefix)


def filter_objects_for_creator(model, user, queryset, filter_field_prefix=''):
    if isinstance(user, AnonymousUser):
        return queryset.none()
    else:
        is_creator = {
            filter_field_prefix + 'creator': user
        }
        return queryset.filter(Q(**is_creator))


def filter_objects_for_user(model, user, queryset, filter_field_prefix=''):
    '''
    Returns a subset of the queryset, filtered on visibility.
    '''
    is_public = {
        filter_field_prefix + 'visibility': Visibility.PUBLIC
    }
    if isinstance(user, AnonymousUser):
        return queryset.filter(**is_public)
    else:
        #groups = user.groups.all()
        ### FIX A BUG IN DJANGO 1.4.3: EmptyManager on AnonymousUser causes
        ### an EmptyQuerySet to be returned, which lacks a model, and thus a model._meta.
        ### This will raise an error when included in a join Query like below.
        ### Fixed in https://code.djangoproject.com/ticket/19184 .
        #if not groups:
        #    groups = []

        current_user_usergroups = UserGroup.objects.filter(Q(members=user) | Q(managers=user)).distinct()

        is_creator = {
            filter_field_prefix + 'creator': user
        }
        common_usergroup = {
            filter_field_prefix + 'visibility': Visibility.USERGROUPS,
            filter_field_prefix + 'creator__managed_user_groups__in': current_user_usergroups,
            filter_field_prefix + 'creator__user_group_memberships__in': current_user_usergroups
        }
        result = queryset.filter(
            Q(**is_public) |
            Q(**is_creator) |
            Q(**common_usergroup)
        )
        return result
