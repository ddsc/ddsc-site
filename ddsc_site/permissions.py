from rest_framework import permissions

from ddsc_site.models import (
    Collage,
    CollageItem,
    Workspace,
    WorkspaceItem,
    Annotation
)


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    def has_permission(self, request, view, obj=None):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # "Read" access is handled by the filter
            return True
        else:
            # Write permission need to be checked.
            if obj is not None:
                # An object is passed, which allows us to check whether the
                # user has permission on it.
                if obj.pk is None:
                    # New object?
                    return True
                else:
                    # Update permissions are only allowed to the
                    # original creator of things
                    if view.model is Workspace:
                        return obj.creator == request.user
                    elif view.model is WorkspaceItem:
                        return obj.workspace.creator == request.user
                    elif view.model is Collage:
                        return obj.creator == request.user
                    elif view.model is CollageItem:
                        return obj.collage.creator == request.user
                    elif view.model is Annotation:
                        return obj.username == request.user.username
                    else:
                        return False
            else:
                # No object requested, it must be some custom (non-model) view.
                # Allow it.
                return True
        # Function shouldve returned by now.
        # Return False anyway in case a developer introduces a bug above.
        return False
