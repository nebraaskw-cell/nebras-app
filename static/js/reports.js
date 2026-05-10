async function loadCircleReport() {
    const id = document.getElementById("circleSelect")?.value;
    if (!id) return;
    showLoading();
    try {
        const res = await fetch(`/api/v1/reports/circles/${id}/`);
        if (!res.ok) throw new Error("request_failed");
        const data = await res.json();
        renderCircleReport(data);
        setExportButtonState("circleExportBtn", true);
    } catch (_err) {
        showError("فشل في تحميل تقرير الحلقة");
    }
}

async function loadStudentReport(directId) {
    const id = directId || document.getElementById("studentSelect")?.value;
    if (!id) return;
    showLoading();
    try {
        const res = await fetch(`/api/v1/reports/students/${id}/`);
        if (!res.ok) throw new Error("request_failed");
        const data = await res.json();
        renderStudentReport(data);
        setExportButtonState("studentExportBtn", true);
    } catch (_err) {
        showError("فشل في تحميل تقرير الطالب");
    }
}

function loadParentStudentReport() {
    const id = document.getElementById("parentStudentSelect")?.value;
    return loadStudentReport(id);
}

async function loadAnalytics() {
    const from = document.getElementById("fromDate")?.value || "";
    const to = document.getElementById("toDate")?.value || "";
    showLoading();
    try {
        const res = await fetch(`/api/v1/reports/analytics/registrations/?from=${from}&to=${to}`);
        if (!res.ok) throw new Error("request_failed");
        const data = await res.json();
        renderAnalyticsReport(data);
    } catch (_err) {
        showError("فشل في تحميل الإحصائيات");
    }
}

function exportCircleReport() {
    const id = document.getElementById("circleSelect")?.value;
    if (id) window.location.href = `/api/v1/reports/circles/${id}/excel/`;
}

function exportStudentReport(directId) {
    const id = directId || document.getElementById("studentSelect")?.value;
    if (id) window.location.href = `/api/v1/reports/students/${id}/excel/`;
}

function exportParentStudentReport() {
    const id = document.getElementById("parentStudentSelect")?.value;
    return exportStudentReport(id);
}

function exportAnalytics() {
    const from = document.getElementById("fromDate")?.value || "";
    const to = document.getElementById("toDate")?.value || "";
    const params = new URLSearchParams();
    if (from) params.set("from", from);
    if (to) params.set("to", to);
    const query = params.toString();
    window.location.href = `/api/v1/reports/analytics/registrations/excel/${query ? `?${query}` : ""}`;
}

function setExportButtonState(id, enabled) {
    const button = document.getElementById(id);
    if (button) button.disabled = !enabled;
}

function showLoading() {
    document.getElementById("placeholderContent")?.classList.add("d-none");
    document.getElementById("reportContent")?.classList.add("d-none");
    document.getElementById("loadingSpinner")?.classList.remove("d-none");
}

function showError(msg) {
    document.getElementById("loadingSpinner")?.classList.add("d-none");
    const content = document.getElementById("reportContent");
    content.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
    content.classList.remove("d-none");
}

function renderCircleReport(data) {
    document.getElementById("loadingSpinner")?.classList.add("d-none");
    const content = document.getElementById("reportContent");
    content.innerHTML = `
        <h4 class="mb-4">تقرير حلقة: ${data.circle.name_ar}</h4>
        <div class="row g-3 mb-4">
            <div class="col-md-6">
                <div class="p-3 border rounded"><p class="mb-1 text-muted">المعلم</p><p class="fw-bold mb-0">${data.circle.teacher || "غير محدد"}</p></div>
            </div>
            <div class="col-md-6">
                <div class="p-3 border rounded"><p class="mb-1 text-muted">المحافظة</p><p class="fw-bold mb-0">${data.circle.governorate}</p></div>
            </div>
        </div>
        <p class="text-center fw-bold">نسبة الحضور الإجمالية: ${data.attendance.present_pct}%</p>
    `;
    content.classList.remove("d-none");
}

function renderStudentReport(data) {
    document.getElementById("loadingSpinner")?.classList.add("d-none");
    const content = document.getElementById("reportContent");
    const rows = (data.history || [])
        .map(
            (h) => `<tr><td>${h.circle}</td><td>${h.attendance.present} / ${h.attendance.total}</td><td>${h.attendance.attendance_rate_pct}%</td><td>${h.enrollment_status}</td></tr>`
        )
        .join("");
    content.innerHTML = `
        <h4 class="mb-4">تقرير الطالب: ${data.student.name}</h4>
        <div class="table-responsive">
            <table class="table table-sm">
                <thead><tr><th>الحلقة</th><th>الحضور</th><th>النسبة</th><th>الحالة</th></tr></thead>
                <tbody>${rows || '<tr><td colspan="4" class="text-center">لا يوجد سجل تاريخي</td></tr>'}</tbody>
            </table>
        </div>
    `;
    content.classList.remove("d-none");
}

function renderAnalyticsReport(data) {
    document.getElementById("loadingSpinner")?.classList.add("d-none");
    const content = document.getElementById("reportContent");
    content.innerHTML = `
        <h4 class="mb-4">إحصائيات التسجيل</h4>
        <p class="text-muted">الفترة من ${data.period.from} إلى ${data.period.to}</p>
        <div class="row text-center g-3 mb-4">
            <div class="col-md-4"><div class="nebras-card p-3"><div class="h2 mb-0">${data.total_registrations}</div><small>إجمالي المسجلين</small></div></div>
            <div class="col-md-4"><div class="nebras-card p-3"><div class="h2 mb-0 text-success">${data.by_status.approved}</div><small>تم قبولهم</small></div></div>
            <div class="col-md-4"><div class="nebras-card p-3"><div class="h2 mb-0 text-info">${data.approval_rate_pct}%</div><small>نسبة القبول</small></div></div>
        </div>
    `;
    content.classList.remove("d-none");
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("circleSelect")?.addEventListener("change", () => {
        setExportButtonState("circleExportBtn", Boolean(document.getElementById("circleSelect")?.value));
    });
    document.getElementById("studentSelect")?.addEventListener("change", () => {
        setExportButtonState("studentExportBtn", Boolean(document.getElementById("studentSelect")?.value));
    });
});
