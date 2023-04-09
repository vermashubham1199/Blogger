from rest_framework.permissions import BasePermission
from blog.tests import pint


class OwnerPermission(BasePermission):
     

    def has_permission(self, request, view):
        if request.method == "POST":
            if request.user.is_authenticated:
                return super().has_permission(request, view)
            else:
                return False
        return super().has_permission(request, view)
          
    
    
    def has_object_permission(self, request, view, obj):
        pint(obj, "permission.py ownerpermission1")
        if request.method in ["PUT", "PATCH", "DELETE",]:
            if request.user == obj.owner:
                return super().has_object_permission(request, view, obj)
            return False


class OwnerPermission2(BasePermission):
     

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return super().has_permission(request, view)
        else:
            return False
          
    
    def has_object_permission(self, request, view, obj):
        pint(obj, "permission.py top line")
        if request.method in ["PATCH", "DELETE","GET", "POST"]:
            pint(request.user, "permission.py before if", obj.owner)
            if request.user == obj.owner:
                pint(request.user, "permission.py", obj.owner)
                return super().has_object_permission(request, view, obj)
            return False
        elif request.method == "PUT":
            return False