document.addEventListener('DOMContentLoaded', () => {
    loadLogs();
});

async function loadLogs() {
    const tableBody = document.getElementById('logsTableBody');
    const noLogsMsg = document.getElementById('noLogsMsg');
    const statTotal = document.getElementById('statTotal');
    const statSuccess = document.getElementById('statSuccess');
    const statFailed = document.getElementById('statFailed');

    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();

        if (!logs || logs.length === 0) {
            tableBody.innerHTML = '';
            noLogsMsg.classList.remove('hidden');
            return;
        }

        noLogsMsg.classList.add('hidden');

        let successCount = 0;
        let failedCount = 0;

        tableBody.innerHTML = logs.map(log => {
            const isSent = log.status === 'sent';
            if (isSent) successCount++; else failedCount++;

            // Extract error message if failed
            let signal = 'Success signal received';
            if (!isSent) {
                signal = log.response?.error?.message || 'Upstream API error';
            }

            return `
                <tr class="hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-4 font-medium text-slate-900">+${log.phone}</td>
                    <td class="px-6 py-4 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${isSent ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                            ${log.status}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-slate-500 text-xs">${log.timestamp}</td>
                    <td class="px-6 py-4 text-xs text-slate-600 truncate max-w-[200px]" title="${signal}">${signal}</td>
                </tr>
            `;
        }).join('');

        // Update stats
        statTotal.textContent = logs.length;
        statSuccess.textContent = successCount;
        statFailed.textContent = failedCount;

    } catch (err) {
        console.error("Critical: Failed to sync logs with engine.", err);
    }
}

document.getElementById('broadcastForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // UI State: Executing
    submitBtn.disabled = true;
    btnText.textContent = 'Transmitting...';
    loadingSpinner.classList.remove('hidden');

    const variables = document.getElementById('variables').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s !== "");

    const numbers = document.getElementById('numbers').value
        .split(/[,\n]/)
        .map(s => s.trim())
        .filter(s => s !== "");

    const payload = {
        template_name: document.getElementById('template_name').value,
        language: document.getElementById('language').value,
        variables: variables,
        numbers: numbers
    };

    try {
        const response = await fetch('/api/send-campaign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        // Final refresh
        await loadLogs();

    } catch (err) {
        console.error("Campaign execution interrupted.", err);
        alert("Transmission error. See console for details.");
    } finally {
        // Reset UI State
        submitBtn.disabled = false;
        btnText.textContent = 'Execute Campaign';
        loadingSpinner.classList.add('hidden');
    }
});
