const caseForm = document.querySelector("#case-form");
const caseList = document.querySelector("#case-list");
const caseIdInput = document.querySelector("#case-id");
const caseNumberInput = document.querySelector("#case-number");
const titleInput = document.querySelector("#title");
const summaryInput = document.querySelector("#summary");
const statusInput = document.querySelector("#status");
const priorityInput = document.querySelector("#priority");
const riskLevelInput = document.querySelector("#risk-level");
const openedDateInput = document.querySelector("#opened-date");
const nextReviewDateInput = document.querySelector("#next-review-date");
const formHeading = document.querySelector("#form-heading");
const formMessage = document.querySelector("#form-message");
const cancelEditButton = document.querySelector("#cancel-edit");
const refreshButton = document.querySelector("#refresh-cases");
const searchInput = document.querySelector("#search-cases");
const statusFilter = document.querySelector("#status-filter");

let cases = [];


function getToday() {
    return new Date().toISOString().split("T")[0];
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function createClassName(value) {
    return String(value ?? "")
        .trim()
        .toLowerCase()
        .replaceAll(" ", "-");
}


function formatDate(value) {
    if (!value) {
        return "Not scheduled";
    }

    const [year, month, day] = value.split("-");

    return `${month}/${day}/${year}`;
}


function showMessage(message, isError = false) {
    formMessage.textContent = message;
    formMessage.classList.toggle("error", isError);
}


function resetForm() {
    caseForm.reset();
    caseIdInput.value = "";
    formHeading.textContent = "Create New Case";
    cancelEditButton.classList.add("hidden");

    statusInput.value = "Open";
    priorityInput.value = "Routine";
    riskLevelInput.value = "Undetermined";
    openedDateInput.value = getToday();

    showMessage("");
}


function updateStatistics() {
    const elevatedPriorities = ["Elevated", "High", "Critical"];

    document.querySelector("#total-cases").textContent = cases.length;

    document.querySelector("#open-cases").textContent = cases.filter(
        (caseItem) => caseItem.status === "Open"
    ).length;

    document.querySelector("#elevated-cases").textContent = cases.filter(
        (caseItem) => elevatedPriorities.includes(caseItem.priority)
    ).length;

    document.querySelector("#critical-cases").textContent = cases.filter(
        (caseItem) => caseItem.risk_level === "Critical"
    ).length;
}


function getFilteredCases() {
    const searchTerm = searchInput.value.trim().toLowerCase();
    const selectedStatus = statusFilter.value;

    return cases.filter((caseItem) => {
        const searchableText = [
            caseItem.case_number,
            caseItem.title,
            caseItem.summary,
        ]
            .join(" ")
            .toLowerCase();

        const matchesSearch = searchableText.includes(searchTerm);
        const matchesStatus =
            !selectedStatus || caseItem.status === selectedStatus;

        return matchesSearch && matchesStatus;
    });
}


function renderCases() {
    const filteredCases = getFilteredCases();

    if (filteredCases.length === 0) {
        caseList.innerHTML = `
            <p class="empty-state">
                No cases match the current search and filter.
            </p>
        `;
        return;
    }

    caseList.innerHTML = filteredCases
        .map((caseItem) => {
            const riskClass = createClassName(caseItem.risk_level);
            const priorityClass = createClassName(caseItem.priority);

            return `
                <article class="case-card risk-${riskClass}">
                    <div class="case-card-header">
                        <div>
                            <p class="case-number">
                                ${escapeHtml(caseItem.case_number)}
                            </p>

                            <h3>${escapeHtml(caseItem.title)}</h3>
                        </div>

                        <div class="badges">
                            <span class="badge">
                                ${escapeHtml(caseItem.status)}
                            </span>

                            <span class="badge priority-${priorityClass}">
                                Priority: ${escapeHtml(caseItem.priority)}
                            </span>

                            <span class="badge risk-${riskClass}">
                                Risk: ${escapeHtml(caseItem.risk_level)}
                            </span>
                        </div>
                    </div>

                    <p class="case-summary">
                        ${escapeHtml(caseItem.summary)}
                    </p>

                    <div class="case-metadata">
                        <span>
                            Opened: ${formatDate(caseItem.opened_date)}
                        </span>

                        <span>
                            Next review:
                            ${formatDate(caseItem.next_review_date)}
                        </span>

                        <span>
                            Record ID: ${caseItem.id}
                        </span>
                    </div>

                    <div class="case-actions">
                        <button
                            class="secondary-button"
                            type="button"
                            data-action="edit"
                            data-case-id="${caseItem.id}"
                        >
                            Edit
                        </button>

                        <button
                            class="danger-button"
                            type="button"
                            data-action="delete"
                            data-case-id="${caseItem.id}"
                        >
                            Delete
                        </button>
                    </div>
                </article>
            `;
        })
        .join("");
}


async function getErrorMessage(response) {
    try {
        const responseData = await response.json();

        if (typeof responseData.detail === "string") {
            return responseData.detail;
        }

        if (Array.isArray(responseData.detail)) {
            return responseData.detail
                .map((error) => error.msg)
                .join(" ");
        }
    } catch {
        return "The server returned an unexpected response.";
    }

    return "The request could not be completed.";
}


async function loadCases() {
    caseList.innerHTML = `
        <p class="empty-state">Loading cases...</p>
    `;

    try {
        const response = await fetch("/cases");

        if (!response.ok) {
            throw new Error(await getErrorMessage(response));
        }

        cases = await response.json();

        updateStatistics();
        renderCases();
    } catch (error) {
        caseList.innerHTML = `
            <p class="empty-state">
                Unable to load cases: ${escapeHtml(error.message)}
            </p>
        `;
    }
}


function startEditing(caseId) {
    const selectedCase = cases.find(
        (caseItem) => caseItem.id === caseId
    );

    if (!selectedCase) {
        return;
    }

    caseIdInput.value = selectedCase.id;
    caseNumberInput.value = selectedCase.case_number;
    titleInput.value = selectedCase.title;
    summaryInput.value = selectedCase.summary;
    statusInput.value = selectedCase.status;
    priorityInput.value = selectedCase.priority;
    riskLevelInput.value = selectedCase.risk_level;
    openedDateInput.value = selectedCase.opened_date;
    nextReviewDateInput.value = selectedCase.next_review_date ?? "";

    formHeading.textContent = `Edit ${selectedCase.case_number}`;
    cancelEditButton.classList.remove("hidden");
    showMessage("");

    caseForm.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


async function deleteCase(caseId) {
    const selectedCase = cases.find(
        (caseItem) => caseItem.id === caseId
    );

    if (!selectedCase) {
        return;
    }

    const confirmed = window.confirm(
        `Delete case ${selectedCase.case_number}? This cannot be undone.`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/cases/${caseId}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            throw new Error(await getErrorMessage(response));
        }

        if (Number(caseIdInput.value) === caseId) {
            resetForm();
        }

        await loadCases();
    } catch (error) {
        window.alert(`Unable to delete case: ${error.message}`);
    }
}


caseForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const caseId = caseIdInput.value;

    const caseData = {
        case_number: caseNumberInput.value.trim(),
        title: titleInput.value.trim(),
        summary: summaryInput.value.trim(),
        status: statusInput.value,
        priority: priorityInput.value,
        risk_level: riskLevelInput.value,
        opened_date: openedDateInput.value,
        next_review_date: nextReviewDateInput.value || null,
    };

    const requestUrl = caseId ? `/cases/${caseId}` : "/cases";
    const requestMethod = caseId ? "PATCH" : "POST";

    showMessage(caseId ? "Updating case..." : "Creating case...");

    try {
        const response = await fetch(requestUrl, {
            method: requestMethod,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(caseData),
        });

        if (!response.ok) {
            throw new Error(await getErrorMessage(response));
        }

        resetForm();
        showMessage(
            caseId
                ? "Case updated successfully."
                : "Case created successfully."
        );

        await loadCases();
    } catch (error) {
        showMessage(error.message, true);
    }
});


caseList.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");

    if (!button) {
        return;
    }

    const caseId = Number(button.dataset.caseId);

    if (button.dataset.action === "edit") {
        startEditing(caseId);
    }

    if (button.dataset.action === "delete") {
        deleteCase(caseId);
    }
});


cancelEditButton.addEventListener("click", resetForm);
refreshButton.addEventListener("click", loadCases);
searchInput.addEventListener("input", renderCases);
statusFilter.addEventListener("change", renderCases);

openedDateInput.value = getToday();
loadCases();