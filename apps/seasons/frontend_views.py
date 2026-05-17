from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.http import HttpResponseForbidden

from .models import Season, SeasonCircle, Enrollment
from .forms import SeasonForm, SeasonCircleForm
from apps.accounts.models import User
from apps.seasons.services import enrollment_service

# ----------------------------------------------------
# Admin Authorization Mixin
# ----------------------------------------------------
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Roles.ADMIN

    def handle_no_permission(self):
        return HttpResponseForbidden("غير مسموح بالوصول. هذه الصلاحيات متاحة لمدير النظام فقط.")

class AdminOrTeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in [User.Roles.ADMIN, User.Roles.TEACHER]

    def handle_no_permission(self):
        return HttpResponseForbidden("غير مسموح بالوصول. هذه الصلاحيات متاحة للمدراء والمعلمين فقط.")


# ----------------------------------------------------
# Student Authorization Mixin
# ----------------------------------------------------
class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Roles.STUDENT and self.request.user.registration_status == User.RegistrationStatus.APPROVED

    def handle_no_permission(self):
        return HttpResponseForbidden("يجب أن يكون حسابك مفعل وبصلاحية طالب للوصول لهذه الصفحة.")


# ----------------------------------------------------
# Season Frontend Views (Admin Only)
# ----------------------------------------------------
class SeasonListView(AdminOrTeacherRequiredMixin, ListView):
    model = Season
    template_name = "seasons/list.html"
    context_object_name = "seasons"
    paginate_by = 20
    ordering = ["-start_date"]


class SeasonCreateView(AdminRequiredMixin, CreateView):
    model = Season
    form_class = SeasonForm
    template_name = "seasons/form.html"
    success_url = reverse_lazy("seasons:list")

    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء الموسم بنجاح!")
        return super().form_valid(form)


class SeasonUpdateView(AdminRequiredMixin, UpdateView):
    model = Season
    form_class = SeasonForm
    template_name = "seasons/form.html"

    def get_success_url(self):
        return reverse("seasons:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث الموسم بنجاح!")
        return super().form_valid(form)


class SeasonDetailView(AdminOrTeacherRequiredMixin, DetailView):
    model = Season
    template_name = "seasons/detail.html"
    context_object_name = "season"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Circles assigned to this season
        context["season_circles"] = self.object.season_circles.select_related("circle", "supervisor").all()
        # All enrollments
        context["enrollments"] = self.object.enrollments.select_related("student", "season_circle__circle").all()
        return context


class SeasonDeleteView(AdminRequiredMixin, DeleteView):
    model = Season
    template_name = "seasons/delete_confirm.html"
    success_url = reverse_lazy("seasons:list")

    def delete(self, request, *args, **kwargs):
        season = self.get_object()
        messages.success(request, f"تم حذف موسم '{season.title}' بنجاح!")
        return super().delete(request, *args, **kwargs)


# ----------------------------------------------------
# SeasonCircle Frontend Views (Admin Only)
# ----------------------------------------------------
class SeasonCircleCreateView(AdminRequiredMixin, CreateView):
    model = SeasonCircle
    form_class = SeasonCircleForm
    template_name = "seasons/circle_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["season"] = get_object_or_404(Season, pk=self.kwargs["season_id"])
        return context

    def form_valid(self, form):
        season = get_object_or_404(Season, pk=self.kwargs["season_id"])
        # Check if circle is already added to this season
        if SeasonCircle.objects.filter(season=season, circle=form.instance.circle).exists():
            messages.error(self.request, "هذه الحلقة مضافة بالفعل لهذا الموسم.")
            return self.form_invalid(form)
            
        form.instance.season = season
        messages.success(self.request, "تم ربط الحلقة بالموسم بنجاح!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("seasons:detail", kwargs={"pk": self.kwargs["season_id"]})

class SeasonCircleDeleteView(AdminRequiredMixin, DeleteView):
    model = SeasonCircle
    template_name = "seasons/circle_delete_confirm.html"

    def get_success_url(self):
        return reverse("seasons:detail", kwargs={"pk": self.object.season.pk})

    def delete(self, request, *args, **kwargs):
        season_circle = self.get_object()
        messages.success(request, f"تم إزالة حلقة '{season_circle.circle.name_ar}' من هذا الموسم.")
        return super().delete(request, *args, **kwargs)


# ----------------------------------------------------
# Student Enrollment Frontend Views
# ----------------------------------------------------
class AvailableSeasonsListView(StudentRequiredMixin, ListView):
    model = Season
    template_name = "seasons/student/available.html"
    context_object_name = "seasons"

    def get_queryset(self):
        return Season.objects.filter(status=Season.Status.REGISTRATION_OPEN).order_by("start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass user's current enrollments so we can show "Already Enrolled" status
        user_enrollments = Enrollment.objects.filter(student=self.request.user).values_list("season_id", flat=True)
        context["enrolled_season_ids"] = list(user_enrollments)
        return context


class StudentEnrollView(StudentRequiredMixin, View):
    def post(self, request, season_id):
        season = get_object_or_404(Season, pk=season_id, status=Season.Status.REGISTRATION_OPEN)
        try:
            enrollment = enrollment_service.enroll_student_in_season(
                student=request.user,
                season=season,
                enrolled_by=request.user
            )
            messages.success(request, f"تم تسجيلك مبدئياً في {season.title}. يرجى اختيار الحلقة المناسبة لك الآن.")
            return redirect("seasons:student-select-circle", pk=enrollment.pk)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("seasons:available")


class StudentSelectCircleView(StudentRequiredMixin, DetailView):
    model = Enrollment
    template_name = "seasons/student/select_circle.html"
    context_object_name = "enrollment"

    def get_queryset(self):
        # Only allow the student to access their own enrollment
        return Enrollment.objects.filter(student=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.object
        # Get circles for this season that match the student's gender
        context["available_circles"] = SeasonCircle.objects.filter(
            season=enrollment.season,
            circle__gender=self.request.user.gender
        ).select_related("circle", "supervisor")
        return context

    def post(self, request, pk):
        enrollment = self.get_object()
        season_circle_id = request.POST.get("season_circle_id")
        
        if not season_circle_id:
            messages.error(request, "الرجاء اختيار حلقة.")
            return redirect("seasons:student-select-circle", pk=pk)
            
        season_circle = get_object_or_404(SeasonCircle, pk=season_circle_id, season=enrollment.season)
        
        try:
            enrollment_service.assign_circle_to_enrollment(
                enrollment=enrollment,
                season_circle=season_circle,
                assigned_by=request.user
            )
            messages.success(request, f"تم انضمامك إلى حلقة '{season_circle.circle.name_ar}' بنجاح! حسابك بانتظار اعتماد المشرف.")
            # Redirect to some dashboard or available seasons
            return redirect("seasons:available")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("seasons:student-select-circle", pk=pk)

