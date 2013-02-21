from django.db.models import Q

def objects_for_user_groups(model, user, queryset, group_field='group'):
    '''
    Returns a subset of the model instances, filtered on the groups the user is currently in.
    Instances with a null group are included as well.
    '''
    groups = user.groups.all()
    ### FIX A BUG IN DJANGO 1.4.3: EmptyManager on AnonymousUser causes
    ### an EmptyQuerySet to be returned, which lacks a model, and thus a model._meta.
    ### This will raise an error when included in a join Query like below.
    if not groups:
        groups = []
    return queryset.filter(Q(**{group_field + '__in': groups}) | Q(**{group_field + '__isnull': True}))
