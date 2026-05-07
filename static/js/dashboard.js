document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    // Helper for API calls
    async function apiCall(url, method = 'POST', body = null) {
        const options = {
            method: method,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        if (body) options.body = JSON.stringify(body);
        
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'API request failed');
            }
            return await response.json();
        } catch (error) {
            alert(error.message);
            throw error;
        }
    }

    // Admin: Approve Student
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const studentId = this.dataset.studentId;
            const originalHtml = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> جاري...';
            this.disabled = true;

            try {
                await apiCall(`/api/v1/accounts/students/${studentId}/approve/`);
                
                // Animate removal of the row
                const row = document.getElementById(`student-row-${studentId}`);
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '0';
                row.style.transform = 'translateX(20px)';
                
                setTimeout(() => {
                    row.remove();
                    // Optionally refresh page if table is empty
                    if(document.querySelectorAll('.approve-btn').length === 0) {
                        location.reload();
                    }
                }, 300);
            } catch (error) {
                this.innerHTML = originalHtml;
                this.disabled = false;
            }
        });
    });

    // Teacher: Start Session
    document.querySelectorAll('.start-session-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const sessionId = this.dataset.sessionId;
            const originalHtml = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> جاري...';
            this.disabled = true;

            try {
                await apiCall(`/api/v1/sessions/sessions/${sessionId}/start/`);
                // Reload to show the active session section
                location.reload();
            } catch (error) {
                this.innerHTML = originalHtml;
                this.disabled = false;
            }
        });
    });

    // Teacher: Complete Session
    document.querySelectorAll('.complete-session-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            if(!confirm("هل أنت متأكد من إنهاء هذه الجلسة؟")) return;
            
            const sessionId = this.dataset.sessionId;
            const originalHtml = this.innerHTML;
            this.innerHTML = 'جاري...';
            this.disabled = true;

            try {
                await apiCall(`/api/v1/sessions/sessions/${sessionId}/complete/`);
                location.reload();
            } catch (error) {
                this.innerHTML = originalHtml;
                this.disabled = false;
            }
        });
    });

    // Teacher: Mark Attendance
    document.querySelectorAll('.mark-attendance-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const sessionId = this.dataset.sessionId;
            window.location.href = `/api/v1/attendance/sessions/${sessionId}/summary/`;
        });
    });

    // Admin/Teacher: Approve Parent Link
    document.querySelectorAll('.approve-parent-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const requestId = this.dataset.requestId;
            const originalHtml = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            this.disabled = true;

            try {
                await apiCall(`/api/v1/accounts/parents/${requestId}/approve/`);
                
                const row = document.getElementById(`parent-row-${requestId}`);
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '0';
                row.style.transform = 'translateX(20px)';
                
                setTimeout(() => {
                    row.remove();
                    if(document.querySelectorAll('.approve-parent-btn').length === 0) {
                        location.reload();
                    }
                }, 300);
            } catch (error) {
                this.innerHTML = originalHtml;
                this.disabled = false;
            }
        });
    });
});

