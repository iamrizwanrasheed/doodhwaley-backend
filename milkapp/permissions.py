from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.groups.filter(name = 'Admin').exists():
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj == request.user

class IsUserOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.groups.filter(name = 'Admin').exists():
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.groups.filter(name = 'Admin').exists():
            return True
        return False

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        print(view.action)
        # Read permissions are allowed to any request,
        if request.user.groups.filter(name = 'Admin').exists():
            return True

        return obj.owner == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access only to admin users. Otherwise Read Only
    """

    def has_permission(self, request, view):
        print(view.action)
        return bool((request.user and request.user.groups.filter(name = 'Admin').exists()) or  (request.method in permissions.SAFE_METHODS))


class IsAdminOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    Allows access only to admin users. Otherwise Read Only
    """

    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.groups.filter(name = 'Admin').exists()
            ) 
            or  
            ((request.method in permissions.SAFE_METHODS) and 
            (request.user and
            request.user.is_authenticated)
            )
            )



class IsOrderOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.groups.filter(name = 'Admin').exists():
            return True
        # Write permissions are only allowed to the owner of the snippet.
        if obj.customer.user == request.user:
            return True
        if obj.store.user == request.user:
            return True
        if obj.delivery_boy.user == request.user:
            return True
        return False