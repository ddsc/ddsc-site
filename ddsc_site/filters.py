from django.db.models import Q

def objects_for_user_groups(model, user, group_field='group'):
    '''
    Returns a subset of the model instances, filtered on the groups the user is currently in.
    Instances with a null group are included as well.
    '''
    groups = user.groups.all()
    return model.objects.filter(Q(**{group_field + '__in': groups}) | Q(**{group_field + '__isnull': True}))
