# # permissions.py
# from rest_framework.permissions import BasePermission
#
#
# class IsInGroup(BasePermission):
#     """
#     Allows access only to users in a specific group.
#     """
#
#     def __init__(self, group_name):
#         self.group_name = group_name
#
#     def has_permission(self, request, view):
#         return (
#             request.user
#             and request.user.is_authenticated
#             and request.user.groups.filter(name=self.group_name).exists()
#         )
#
#
# class HasModelPermission(BasePermission):
#     """
#     Uses Django model permissions (add, change, delete, view)
#     """
#
#     def has_permission(self, request, view):
#         # Example: app_label.change_modelname
#         perm_map = {
#             "GET": f"{view.queryset.model._meta.app_label}.view_{view.queryset.model._meta.model_name}",
#             "POST": f"{view.queryset.model._meta.app_label}.add_{view.queryset.model._meta.model_name}",
#             "PUT": f"{view.queryset.model._meta.app_label}.change_{view.queryset.model._meta.model_name}",
#             "PATCH": f"{view.queryset.model._meta.app_label}.change_{view.queryset.model._meta.model_name}",
#             "DELETE": f"{view.queryset.model._meta.app_label}.delete_{view.queryset.model._meta.model_name}",
#         }
#         return request.user.has_perm(perm_map.get(request.method, ""))
