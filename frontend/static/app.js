
const API_BASE = "";

async function fetchStats() {
    const response = await fetch(`${API_BASE}/api/stats`);

    if (!response.ok) {
        throw new Error("Unable to load dashboard statistics.");
    }

    const stats = await response.json();

    document.getElementById("total-transactions").textContent =
        Number(stats.total_transactions || 0).toLocaleString("en-IN");

    document.getElementById("total-amount").textContent =
        new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        }).format(stats.total_amount || 0);

    document.getElementById("successful-transactions").textContent =
        Number(stats.successful_transactions || 0).toLocaleString("en-IN");

    document.getElementById("failed-transactions").textContent =
        Number(stats.failed_transactions || 0).toLocaleString("en-IN");

	document.getElementById("average-amount").textContent =
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(stats.average_amount || 0);

document.getElementById("success-rate").textContent =
    `${stats.success_rate || 0}%`;

document.getElementById("failure-rate").textContent =
    `${stats.failure_rate || 0}%`;

document.getElementById("success-progress").style.width =
    `${stats.success_rate || 0}%`;

document.getElementById("failure-progress").style.width =
    `${stats.failure_rate || 0}%`;

const paymentMethods = document.getElementById("payment-methods");

paymentMethods.innerHTML = stats.payment_methods.map(method => `
    <div class="analytics-row">
        <div>
            <strong>${escapeHTML(method.payment_method)}</strong>
            <span>${method.transaction_count} transaction(s)</span>
        </div>

        <strong>
            ${new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 2
            }).format(method.total_amount)}
        </strong>
    </div>
`).join("");
}


async function fetchTransactions() {
    const status = document.getElementById("status-filter").value;

    const query = status
        ? `?status=${encodeURIComponent(status)}`
        : "";

    const response = await fetch(
        `${API_BASE}/api/transactions${query}`
    );

    if (!response.ok) {
        throw new Error("Unable to load transactions.");
    }

    const transactions = await response.json();

    const table = document.getElementById("transactions-table");

    if (transactions.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="6">No transactions found.</td>
            </tr>
        `;
        return;
    }

    table.innerHTML = transactions.map(transaction => {
        const statusClass =
            transaction.status.toUpperCase() === "SUCCESS"
                ? "status-success"
                : "status-failed";

        const amount = new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: transaction.currency || "INR",
            maximumFractionDigits: 2
        }).format(transaction.transaction_amount);

        return `
            <tr>
                <td>${escapeHTML(transaction.transaction_id)}</td>
                <td>${escapeHTML(transaction.customer_id)}</td>
                <td>${escapeHTML(transaction.merchant_id)}</td>
                <td>${amount}</td>
                <td>${escapeHTML(transaction.payment_method)}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        ${escapeHTML(transaction.status)}
                    </span>
                </td>
            </tr>
        `;
    }).join("");
}


function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

async function fetchSuspiciousTransactions() {
    const response = await fetch("/api/suspicious-transactions");

    if (!response.ok) {
        throw new Error("Unable to load suspicious transactions.");
    }

    const transactions = await response.json();
    const table = document.getElementById("suspicious-table");

    if (transactions.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="5">No suspicious transactions detected.</td>
            </tr>
        `;
        return;
    }

    table.innerHTML = transactions.map(transaction => `
        <tr>
            <td>${escapeHTML(transaction.transaction_id)}</td>
            <td>${escapeHTML(transaction.customer_id)}</td>
            <td>${new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: transaction.currency || "INR"
            }).format(transaction.transaction_amount)}</td>
            <td>
                <span class="status-badge status-failed">
                    ${escapeHTML(transaction.risk_level)}
                </span>
            </td>
            <td>${transaction.fraud_reasons.map(escapeHTML).join(", ")}</td>
        </tr>
    `).join("");
}


async function refreshDashboard() {
    try {
        await Promise.all([
            fetchStats(),
            fetchTransactions(),
	    fetchSuspiciousTransactions()
        ]);
    } catch (error) {
        console.error(error);

        document.getElementById("transactions-table").innerHTML = `
            <tr>
                <td colspan="6">Unable to load dashboard data. Please refresh.</td>
            </tr>
        `;
    }
}


document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("status-filter")
        .addEventListener("change", fetchTransactions);

    refreshDashboard();
});
