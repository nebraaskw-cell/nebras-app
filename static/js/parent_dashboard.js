async function requestParentLink(event) {
    event.preventDefault();
    const btn = event.target.querySelector("button[type='submit']");
    if (btn) btn.disabled = true;

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
            window.location.reload();
            return;
        }

        const data = await res.json();
        alert(`حدث خطأ: ${JSON.stringify(data)}`);
    } catch (err) {
        console.error(err);
        alert("حدث خطأ في الاتصال");
    } finally {
        if (btn) btn.disabled = false;
    }
}
