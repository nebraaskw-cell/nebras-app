async function requestParentLink(event) {
    event.preventDefault();
    const btn = event.target.querySelector("button[type='submit']");
    if (btn) btn.disabled = true;
    showParentLinkFeedback("", "info", true);

    try {
        const res = await fetch("/api/v1/accounts/parents/link-request/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
            },
            body: JSON.stringify({
                student_username: document.getElementById("studentUsername")?.value,
                notes: document.getElementById("linkNotes")?.value,
            }),
        });

        if (res.ok) {
            showParentLinkFeedback("تم إرسال طلب الربط بنجاح. سيتم تحديث الصفحة الآن.", "success");
            window.location.reload();
            return;
        }

        const data = await res.json();
        showParentLinkFeedback(`تعذر إرسال الطلب: ${formatApiError(data)}`, "danger");
    } catch (err) {
        console.error(err);
        showParentLinkFeedback("حدث خطأ في الاتصال. حاول مرة أخرى.", "danger");
    } finally {
        if (btn) btn.disabled = false;
    }
}

function showParentLinkFeedback(message, type, hide = false) {
    const target = document.getElementById("parentLinkFeedback");
    if (!target) return;
    if (hide) {
        target.className = "d-none";
        target.innerHTML = "";
        return;
    }
    target.className = `alert alert-${type} py-2 mb-0`;
    target.textContent = message;
}

function formatApiError(data) {
    if (!data) return "حدث خطأ غير معروف.";
    if (typeof data === "string") return data;
    if (data.non_field_errors) return data.non_field_errors.join(" ");
    if (data.detail) return data.detail;
    return Object.values(data).flat().join(" ");
}
