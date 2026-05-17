from django.db import models
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets

from apps.core.permissions import ReadOnlyOrAdminRole
from .models import Circle
from .serializers import CircleSerializer
from .services import query_service


# ----------------------------------------------------
# Forms
# ----------------------------------------------------
class CircleForm(forms.ModelForm):
    class Meta:
        model = Circle
        fields = [
            "name",
            "name_ar",
            "gender",
            "description",
            "start_date",
            "end_date",
            "status",
            "governorate",
            "teacher",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Example: abu_bakr"}),
            "name_ar": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثال: حلقة أبي بكر الصديق"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "نبذة عن الحلقة وأهدافها..."}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "governorate": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


# ----------------------------------------------------
# Admin Authorization Mixin
# ----------------------------------------------------
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == "admin"

    def handle_no_permission(self):
        return HttpResponseForbidden("غير مسموح بالوصول. هذه الصلاحيات متاحة لمدير النظام فقط.")


# ----------------------------------------------------
# Frontend Views
# ----------------------------------------------------
class CircleListView(ListView):
    model = Circle
    template_name = "circles/list.html"
    context_object_name = "circles"
    paginate_by = 20

    def get_queryset(self):
        # Admins see all circles, others see open circles or query_service get_active_circles
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return Circle.objects.all().order_by("governorate", "name")
        return query_service.get_active_circles().order_by("governorate", "name")


class CircleCreateView(AdminRequiredMixin, CreateView):
    model = Circle
    form_class = CircleForm
    template_name = "circles/form.html"
    success_url = reverse_lazy("circles:list")

    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء الحلقة بنجاح!")
        return super().form_valid(form)


class CircleUpdateView(AdminRequiredMixin, UpdateView):
    model = Circle
    form_class = CircleForm
    template_name = "circles/form.html"
    success_url = reverse_lazy("circles:list")

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات الحلقة بنجاح!")
        return super().form_valid(form)


class CircleDeleteView(AdminRequiredMixin, DeleteView):
    model = Circle
    template_name = "circles/delete_confirm.html"
    success_url = reverse_lazy("circles:list")

    def delete(self, request, *args, **kwargs):
        circle = self.get_object()
        messages.success(request, f"تم حذف حلقة '{circle.name_ar}' بنجاح!")
        return super().delete(request, *args, **kwargs)


class CircleCloneView(AdminRequiredMixin, View):
    def post(self, request, pk):
        circle = get_object_or_404(Circle, pk=pk)
        
        # Determine a unique English name for the clone
        base_name = circle.name
        count = Circle.objects.filter(name__startswith=base_name).count()
        new_name = f"{base_name}_copy_{count + 1}"
        
        cloned = Circle.objects.create(
            name=new_name,
            name_ar=f"{circle.name_ar} (نسخة)",
            gender=circle.gender,
            description=circle.description,
            start_date=circle.start_date,
            end_date=circle.end_date,
            status=circle.status,
            governorate=circle.governorate,
            teacher=circle.teacher,
            image=circle.image,
        )
        
        messages.success(request, f"تم نسخ حلقة '{circle.name_ar}' بنجاح إلى '{cloned.name_ar}'!")
        return redirect("circles:list")


# ----------------------------------------------------
# API ViewSets
# ----------------------------------------------------
class CircleViewSet(viewsets.ModelViewSet):
    serializer_class = CircleSerializer
    permission_classes = [ReadOnlyOrAdminRole]
    filterset_fields = ["gender", "governorate", "status"]
    search_fields = ["name", "name_ar", "description"]
    ordering_fields = ["name", "governorate", "created_at"]

    def get_queryset(self):
        return query_service.get_circles()
