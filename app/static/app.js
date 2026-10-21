const state = {
    cases: [],
    selectedCaseId: null,
    selectedCase: null,
    currentUser: null,
    sortBy: "review-urgency",
};

const elements = {
        authenticationScreen: document.getElementById(
        "authenticationScreen"
    ),
    applicationShell: document.getElementById(
        "applicationShell"
    ),
    loginPanel: document.getElementById("loginPanel"),
    bootstrapPanel: document.getElementById(
        "bootstrapPanel"
    ),
    loginForm: document.getElementById("loginForm"),
    loginUsername: document.getElementById(
        "loginUsername"
    ),
    loginPassword: document.getElementById(
        "loginPassword"
    ),
    bootstrapForm: document.getElementById(
        "bootstrapForm"
    ),
    bootstrapUsername: document.getElementById(
        "bootstrapUsername"
    ),
    bootstrapFullName: document.getElementById(
        "bootstrapFullName"
    ),
    bootstrapPassword: document.getElementById(
        "bootstrapPassword"
    ),
    bootstrapPasswordConfirmation:
        document.getElementById(
            "bootstrapPasswordConfirmation"
        ),
    showBootstrapButton: document.getElementById(
        "showBootstrapButton"
    ),
    showLoginButton: document.getElementById(
        "showLoginButton"
    ),
    authenticationMessage: document.getElementById(
        "authenticationMessage"
    ),
    currentUserName: document.getElementById(
        "currentUserName"
    ),
    currentUserRole: document.getElementById(
        "currentUserRole"
    ),
    logoutButton: document.getElementById(
        "logoutButton"
    ),

    totalCases: document.getElementById("totalCases"),
    openCases: document.getElementById("openCases"),
    elevatedCases: document.getElementById("elevatedCases"),
    criticalCases: document.getElementById("criticalCases"),

    caseForm: document.getElementById("caseForm"),
    caseFormTitle: document.getElementById("caseFormTitle"),
    editingCaseId: document.getElementById("editingCaseId"),
    caseNumber: document.getElementById("caseNumber"),
    caseTitle: document.getElementById("caseTitle"),
    caseSummary: document.getElementById("caseSummary"),
    caseStatus: document.getElementById("caseStatus"),
    casePriority: document.getElementById("casePriority"),
    caseRiskLevel: document.getElementById("caseRiskLevel"),
    openedDate: document.getElementById("openedDate"),
nextReviewDate: document.getElementById("nextReviewDate"),

assignedAnalyst: document.getElementById(
    "assignedAnalyst"
),

responsibleTeam: document.getElementById(
    "responsibleTeam"
),

cancelEditButton: document.getElementById(
        "cancelEditButton"
    ),

    refreshButton: document.getElementById("refreshButton"),
    caseRegisterTitle: document.getElementById(
        "caseRegisterTitle"
    ),
    searchInput: document.getElementById("searchInput"),
statusFilter: document.getElementById("statusFilter"),
archiveFilter: document.getElementById("archiveFilter"),

analystFilter: document.getElementById(
    "analystFilter"
),

teamFilter: document.getElementById(
    "teamFilter"
),
reviewFilter: document.getElementById("reviewFilter"),

sortSelect: null,
    caseList: document.getElementById("caseList"),

    analysisWorkspace: document.getElementById(
        "analysisWorkspace"
    ),
    closeWorkspaceButton: document.getElementById(
        "closeWorkspaceButton"
    ),
    selectedCaseTitle: document.getElementById(
        "selectedCaseTitle"
    ),
    selectedCaseSummary: document.getElementById(
        "selectedCaseSummary"
    ),

    indicatorForm: document.getElementById("indicatorForm"),
    indicatorType: document.getElementById("indicatorType"),
    indicatorDescription: document.getElementById(
        "indicatorDescription"
    ),
    indicatorSource: document.getElementById(
        "indicatorSource"
    ),
    indicatorCredibility: document.getElementById(
        "indicatorCredibility"
    ),
    indicatorObservedDate: document.getElementById(
        "indicatorObservedDate"
    ),
    indicatorList: document.getElementById("indicatorList"),

    assessmentForm: document.getElementById("assessmentForm"),
    threatLevel: document.getElementById("threatLevel"),
    vulnerabilityLevel: document.getElementById(
        "vulnerabilityLevel"
    ),
    impactLevel: document.getElementById("impactLevel"),
    overallRisk: document.getElementById("overallRisk"),
    assessmentRationale: document.getElementById(
        "assessmentRationale"
    ),
    recommendedAction: document.getElementById(
        "recommendedAction"
    ),
    assessedBy: document.getElementById("assessedBy"),
    assessmentDate: document.getElementById(
        "assessmentDate"
    ),
    assessmentList: document.getElementById(
        "assessmentList"
    ),

    mitigationForm: document.getElementById("mitigationForm"),
    mitigationTitle: document.getElementById(
        "mitigationTitle"
    ),
    mitigationDescription: document.getElementById(
        "mitigationDescription"
    ),
    mitigationOwner: document.getElementById(
        "mitigationOwner"
    ),
    mitigationPriority: document.getElementById(
        "mitigationPriority"
    ),
    mitigationStatus: document.getElementById(
        "mitigationStatus"
    ),
    mitigationDueDate: document.getElementById(
        "mitigationDueDate"
    ),
   mitigationList: document.getElementById(
    "mitigationList"
),

reviewForm: document.getElementById(
    "reviewForm"
),

reviewDate: document.getElementById(
    "reviewDate"
),

reviewedBy: document.getElementById(
    "reviewedBy"
),

reviewFindings: document.getElementById(
    "reviewFindings"
),

reviewNextDate: document.getElementById(
    "reviewNextDate"
),

reviewList: document.getElementById(
    "reviewList"
),

activityList: document.getElementById(
    "activityList"
),
    toast: document.getElementById("toast"),
};

function hasRole(...allowedRoles) {
    return Boolean(
        state.currentUser &&
        allowedRoles.includes(state.currentUser.role)
    );
}


function canEditCases() {
    return hasRole(
        "Administrator",
        "Analyst"
    );
}


function canCreateReviewsAndAssessments() {
    return hasRole(
        "Administrator",
        "Analyst",
        "Reviewer"
    );
}


function canDeleteRecords() {
    return hasRole("Administrator");
}

function applyRolePermissions() {
    const caseFormPanel =
        elements.caseForm.closest(".panel");

    caseFormPanel.classList.toggle(
        "hidden",
        !canEditCases()
    );

    elements.indicatorForm.classList.toggle(
        "hidden",
        !canEditCases()
    );

    elements.mitigationForm.classList.toggle(
        "hidden",
        !canEditCases()
    );

    elements.assessmentForm.classList.toggle(
        "hidden",
        !canCreateReviewsAndAssessments()
    );

    elements.reviewForm.classList.toggle(
        "hidden",
        !canCreateReviewsAndAssessments()
    );
}

function createSortControl() {
    const filterRow = elements.statusFilter?.closest(
        ".filter-row"
    );

    if (!filterRow || document.getElementById("caseSort")) {
        return;
    }

    const sortSelect = document.createElement("select");

    sortSelect.id = "caseSort";
    sortSelect.setAttribute("aria-label", "Sort cases");

    sortSelect.innerHTML = `
        <option value="review-urgency">
            Review urgency
        </option>

        <option value="updated-newest">
            Recently updated
        </option>

        <option value="opened-newest">
            Newest cases
        </option>

        <option value="priority-high">
            Highest priority
        </option>

        <option value="case-number">
            Case number
        </option>
    `;

    sortSelect.value = state.sortBy;
    filterRow.appendChild(sortSelect);
    elements.sortSelect = sortSelect;
}


function today() {
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


function formatDate(value) {
    if (!value) {
        return "Not scheduled";
    }

    const parts = value.split("-");

    if (parts.length !== 3) {
        return value;
    }

    return `${parts[1]}/${parts[2]}/${parts[0]}`;
}


function formatDateTime(value) {
    if (!value) {
        return "Unknown time";
    }

    const parsedDate = new Date(value);

    if (Number.isNaN(parsedDate.getTime())) {
        return value;
    }

    return parsedDate.toLocaleString([], {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
    });
}


function dateOnly(value) {
    if (!value) {
        return null;
    }

    const parsedDate = new Date(`${value}T00:00:00`);

    return Number.isNaN(parsedDate.getTime())
        ? null
        : parsedDate;
}


function reviewStatus(caseItem) {
    if (
        ["Closed", "Mitigated"].includes(caseItem.status)
    ) {
        return {
            key: "inactive",
            label: "Review not required",
            rank: 5,
        };
    }

    const reviewDate = dateOnly(
        caseItem.next_review_date
    );

    if (!reviewDate) {
        return {
            key: "unscheduled",
            label: "Review not scheduled",
            rank: 3,
        };
    }

    const currentDate = dateOnly(today());
    const millisecondsPerDay = 24 * 60 * 60 * 1000;

    const daysUntilReview = Math.round(
        (reviewDate - currentDate) /
            millisecondsPerDay
    );

    if (daysUntilReview < 0) {
        const overdueDays = Math.abs(daysUntilReview);

        return {
            key: "overdue",
            label: `${overdueDays} day${
                overdueDays === 1 ? "" : "s"
            } overdue`,
            rank: 0,
        };
    }

    if (daysUntilReview === 0) {
        return {
            key: "due-today",
            label: "Review due today",
            rank: 1,
        };
    }

    if (daysUntilReview <= 7) {
        return {
            key: "due-soon",
            label: `Review due in ${daysUntilReview} day${
                daysUntilReview === 1 ? "" : "s"
            }`,
            rank: 2,
        };
    }

    return {
        key: "scheduled",
        label: `Review scheduled ${formatDate(
            caseItem.next_review_date
        )}`,
        rank: 4,
    };
}


function mitigationDeadlineStatus(mitigation) {
    if (
        ["Completed", "Cancelled"].includes(
            mitigation.status
        )
    ) {
        return {
            key: "inactive",
            label: mitigation.status,
        };
    }

    const dueDate = dateOnly(mitigation.due_date);

    if (!dueDate) {
        return {
            key: "unscheduled",
            label: "Due date not scheduled",
        };
    }

    const currentDate = dateOnly(today());
    const millisecondsPerDay = 24 * 60 * 60 * 1000;

    const daysUntilDue = Math.round(
        (dueDate - currentDate) /
            millisecondsPerDay
    );

    if (daysUntilDue < 0) {
        const overdueDays = Math.abs(daysUntilDue);

        return {
            key: "overdue",
            label: `${overdueDays} day${
                overdueDays === 1 ? "" : "s"
            } overdue`,
        };
    }

    if (daysUntilDue === 0) {
        return {
            key: "due-today",
            label: "Due today",
        };
    }

    if (daysUntilDue <= 7) {
        return {
            key: "due-soon",
            label: `Due in ${daysUntilDue} day${
                daysUntilDue === 1 ? "" : "s"
            }`,
        };
    }

    return {
        key: "scheduled",
        label: `Due ${formatDate(
            mitigation.due_date
        )}`,
    };
}


function compareCases(firstCase, secondCase) {
    const priorityRank = {
        Critical: 0,
        High: 1,
        Elevated: 2,
        Routine: 3,
    };

    if (state.sortBy === "review-urgency") {
        const rankDifference =
            reviewStatus(firstCase).rank -
            reviewStatus(secondCase).rank;

        if (rankDifference !== 0) {
            return rankDifference;
        }

        return String(
            firstCase.next_review_date ||
                "9999-12-31"
        ).localeCompare(
            String(
                secondCase.next_review_date ||
                    "9999-12-31"
            )
        );
    }

    if (state.sortBy === "updated-newest") {
        return (
            new Date(secondCase.updated_at) -
            new Date(firstCase.updated_at)
        );
    }

    if (state.sortBy === "opened-newest") {
        return String(
            secondCase.opened_date
        ).localeCompare(
            String(firstCase.opened_date)
        );
    }

    if (state.sortBy === "priority-high") {
        return (
            (priorityRank[firstCase.priority] ?? 99) -
            (priorityRank[secondCase.priority] ?? 99)
        );
    }

    return String(
        firstCase.case_number
    ).localeCompare(
        String(secondCase.case_number),
        undefined,
        {
            numeric: true,
            sensitivity: "base",
        }
    );
}


function levelClass(level) {
    const normalized = String(
        level ?? ""
    ).toLowerCase();

    if (
        normalized === "critical" ||
        normalized === "high"
    ) {
        return "red";
    }

    if (
        normalized === "elevated" ||
        normalized === "moderate"
    ) {
        return "amber";
    }

    if (
        normalized === "low" ||
        normalized === "confirmed" ||
        normalized === "closed" ||
        normalized === "mitigated" ||
        normalized === "completed"
    ) {
        return "green";
    }

    return "";
}


async function apiRequest(url, options = {}) {
    const requestOptions = {
        ...options,
        headers: {
            ...(options.body
                ? {
                    "Content-Type":
                        "application/json",
                }
                : {}),
            ...(options.headers || {}),
        },
    };

    const response = await fetch(
        url,
        requestOptions
    );

    if (response.status === 204) {
        return null;
    }

    const data = await response
        .json()
        .catch(() => null);

    if (!response.ok) {
        let message =
            "The request could not be completed.";

        if (data?.detail) {
            if (Array.isArray(data.detail)) {
                message = data.detail
                    .map((item) => item.msg)
                    .join("; ");
            } else {
                message = data.detail;
            }
        }

                const error = new Error(message);
        error.status = response.status;
        throw error;
    }

    return data;
}

function showAuthenticationMessage(
    message,
    isSuccess = false
) {
    elements.authenticationMessage.textContent =
        message;

    elements.authenticationMessage.classList.remove(
        "hidden",
        "success"
    );

    if (isSuccess) {
        elements.authenticationMessage.classList.add(
            "success"
        );
    }
}


function clearAuthenticationMessage() {
    elements.authenticationMessage.textContent = "";

    elements.authenticationMessage.classList.add(
        "hidden"
    );

    elements.authenticationMessage.classList.remove(
        "success"
    );
}


function showLoginPanel() {
    clearAuthenticationMessage();

    elements.bootstrapPanel.classList.add("hidden");
    elements.loginPanel.classList.remove("hidden");
    elements.loginPassword.value = "";
    elements.loginUsername.focus();
}


function showBootstrapPanel() {
    clearAuthenticationMessage();

    elements.loginPanel.classList.add("hidden");
    elements.bootstrapPanel.classList.remove("hidden");
    elements.bootstrapUsername.focus();
}


function showAuthenticationScreen() {
    state.currentUser = null;

    elements.applicationShell.classList.add("hidden");

    elements.authenticationScreen.classList.remove(
        "hidden"
    );

    showLoginPanel();
}


async function showApplication(user) {
    state.currentUser = user;

    elements.currentUserName.textContent =
        user.full_name;

    elements.currentUserRole.textContent =
        user.role;

    applyRolePermissions();

    elements.authenticationScreen.classList.add(
        "hidden"
    );

    elements.applicationShell.classList.remove(
        "hidden"
    );

    await loadCases();
}


async function submitLogin(event) {
    event.preventDefault();
    clearAuthenticationMessage();

    const submitButton =
        elements.loginForm.querySelector(
            'button[type="submit"]'
        );

    submitButton.disabled = true;
    submitButton.textContent = "Signing In...";

    try {
        const authentication = await apiRequest(
            "/auth/login",
            {
                method: "POST",
                body: JSON.stringify({
                    username:
                        elements.loginUsername.value.trim(),
                    password:
                        elements.loginPassword.value,
                }),
            }
        );

        elements.loginForm.reset();

        const user =
            authentication.user || authentication;

        await showApplication(user);
    } catch (error) {
        showAuthenticationMessage(error.message);
        elements.loginPassword.select();
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Sign In";
    }
}


async function submitBootstrap(event) {
    event.preventDefault();
    clearAuthenticationMessage();

    const password =
        elements.bootstrapPassword.value;

    const confirmation =
        elements.bootstrapPasswordConfirmation.value;

    if (password !== confirmation) {
        showAuthenticationMessage(
            "The passwords do not match."
        );

        elements.bootstrapPasswordConfirmation.select();
        return;
    }

    const submitButton =
        elements.bootstrapForm.querySelector(
            'button[type="submit"]'
        );

    submitButton.disabled = true;
    submitButton.textContent =
        "Creating Administrator...";

    try {
        const username =
            elements.bootstrapUsername.value.trim();

        await apiRequest(
            "/auth/bootstrap",
            {
                method: "POST",
                body: JSON.stringify({
                    username,
                    full_name:
                        elements.bootstrapFullName
                            .value.trim(),
                    password,
                    role: "Administrator",
                }),
            }
        );

        elements.bootstrapForm.reset();
        showLoginPanel();

        elements.loginUsername.value = username;

        showAuthenticationMessage(
            "Administrator account created. Sign in to continue.",
            true
        );

        elements.loginPassword.focus();
    } catch (error) {
        showAuthenticationMessage(error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent =
            "Create Administrator";
    }
}


async function logout() {
    elements.logoutButton.disabled = true;

    try {
        await apiRequest(
            "/auth/logout",
            {
                method: "POST",
            }
        );
    } catch (error) {
        console.error(error);
    } finally {
        state.cases = [];
        state.selectedCaseId = null;
        state.selectedCase = null;

        elements.logoutButton.disabled = false;

        showAuthenticationScreen();

        showAuthenticationMessage(
            "You have been signed out.",
            true
        );
    }
}


async function initializeApplication() {
    try {
        const user = await apiRequest("/auth/me");
        await showApplication(user);
    } catch (error) {
        showAuthenticationScreen();
    }
}

let toastTimer;


function showToast(message, isError = false) {
    clearTimeout(toastTimer);

    elements.toast.textContent = message;
    elements.toast.classList.remove(
        "hidden",
        "error"
    );

    if (isError) {
        elements.toast.classList.add("error");
    }

    toastTimer = setTimeout(() => {
        elements.toast.classList.add("hidden");
    }, 3500);
}


function updateStatistics() {
    const activeCases = state.cases.filter(
        (caseItem) => !caseItem.is_archived
    );

    const activeStatuses = new Set([
        "Open",
        "Monitoring",
    ]);

    const elevatedPriorities = new Set([
        "Elevated",
        "High",
        "Critical",
    ]);

    elements.totalCases.textContent =
        activeCases.length;

    elements.openCases.textContent =
        activeCases.filter(
            (caseItem) =>
                activeStatuses.has(caseItem.status)
        ).length;

    elements.elevatedCases.textContent =
        activeCases.filter(
            (caseItem) =>
                elevatedPriorities.has(
                    caseItem.priority
                )
        ).length;

    elements.criticalCases.textContent =
        activeCases.filter(
            (caseItem) =>
                caseItem.risk_level === "Critical"
        ).length;
}
function filteredCases() {
    const searchTerm = elements.searchInput.value
        .trim()
        .toLowerCase();

        const reviewFilter = elements.reviewFilter.value;
const today = new Date();
today.setHours(0, 0, 0, 0);

const dueSoonCutoff = new Date(today);
dueSoonCutoff.setDate(dueSoonCutoff.getDate() + 7);

    const selectedStatus =
        elements.statusFilter.value;

    const archiveView =
        elements.archiveFilter.value;

    const analystTerm = elements.analystFilter.value
        .trim()
        .toLowerCase();

    const teamTerm = elements.teamFilter.value
        .trim()
        .toLowerCase();

    return state.cases
    .filter((caseItem) => {
        const matchesStatus =
            !selectedStatus ||
            caseItem.status === selectedStatus;

        const searchableText = [
            caseItem.case_number,
            caseItem.title,
            caseItem.summary,
            caseItem.assigned_analyst,
            caseItem.responsible_team,
        ]
            .join(" ")
            .toLowerCase();

        const matchesSearch =
            !searchTerm ||
            searchableText.includes(searchTerm);

        const matchesArchiveView =
            archiveView === "all" ||
            (
                archiveView === "archived" &&
                caseItem.is_archived
            ) ||
            (
                archiveView === "active" &&
                !caseItem.is_archived
            );

        const matchesAnalyst =
            !analystTerm ||
            String(caseItem.assigned_analyst || "")
                .toLowerCase()
                .includes(analystTerm);

        const matchesTeam =
            !teamTerm ||
            String(caseItem.responsible_team || "")
                .toLowerCase()
                .includes(teamTerm);

        const reviewDate = caseItem.next_review_date
            ? new Date(
                `${caseItem.next_review_date}T00:00:00`
            )
            : null;

        let matchesReview = true;

        if (reviewFilter === "missing") {
            matchesReview = reviewDate === null;
        } else if (reviewFilter === "overdue") {
            matchesReview =
                reviewDate !== null &&
                reviewDate < today;
        } else if (reviewFilter === "due-soon") {
            matchesReview =
                reviewDate !== null &&
                reviewDate >= today &&
                reviewDate <= dueSoonCutoff;
        } else if (reviewFilter === "scheduled") {
            matchesReview =
                reviewDate !== null &&
                reviewDate > dueSoonCutoff;
        }

        return (
            matchesStatus &&
            matchesSearch &&
            matchesArchiveView &&
            matchesAnalyst &&
            matchesTeam &&
            matchesReview
        );
    })
    .sort(compareCases);
}

function updateCaseRegisterTitle() {
    const titles = {
        active: "Active Case Register",
        archived: "Archived Case Register",
        all: "Complete Case Register",
    };

    elements.caseRegisterTitle.textContent =
        titles[elements.archiveFilter.value] ||
        titles.active;
}


function renderCases() {
    const cases = filteredCases();

    if (cases.length === 0) {
        elements.caseList.innerHTML = `
            <p class="empty-state">
                No cases match the current filters.
            </p>
        `;

        return;
    }

    elements.caseList.innerHTML = cases
        .map((caseItem) => {
            const selected =
                state.selectedCaseId === caseItem.id
                    ? "selected"
                    : "";

            const priorityClass =
                `priority-${caseItem.priority.toLowerCase()}`;

            const review = reviewStatus(caseItem);

            const archivedClass =
                caseItem.is_archived
                    ? "archived"
                    : "";

            const archiveBadge =
                caseItem.is_archived
                    ? `
                        <span
                            class="badge archived-badge"
                        >
                            Archived
                        </span>
                    `
                    : "";

            const editActions =
                canEditCases()
                    ? (
                        caseItem.is_archived
                            ? `
                                <button
                                    class="small-button restore-button"
                                    type="button"
                                    data-action="restore-case"
                                    data-case-id="${caseItem.id}"
                                >
                                    Restore
                                </button>
                            `
                            : `
                                <button
                                    class="small-button"
                                    type="button"
                                    data-action="edit"
                                    data-case-id="${caseItem.id}"
                                >
                                    Edit
                                </button>

                                <button
                                    class="small-button archive-button"
                                    type="button"
                                    data-action="archive-case"
                                    data-case-id="${caseItem.id}"
                                >
                                    Archive
                                </button>
                            `
                    )
                    : "";

            const deleteAction =
                canDeleteRecords()
                    ? `
                        <button
                            class="danger-button"
                            type="button"
                            data-action="delete-case"
                            data-case-id="${caseItem.id}"
                        >
                            Delete
                        </button>
                    `
                    : "";

            return `
                <article
                    class="case-card ${priorityClass} review-${review.key} ${archivedClass} ${selected}"
                    data-case-id="${caseItem.id}"
                >
                    <div class="case-card-header">
                        <div>
                            <p class="case-number">
                                ${escapeHtml(
                                    caseItem.case_number
                                )}
                            </p>

                            <h3>
                                ${escapeHtml(
                                    caseItem.title
                                )}
                            </h3>
                        </div>

                        <div class="badge-group">
                            ${archiveBadge}

                            <span class="badge">
                                ${escapeHtml(
                                    caseItem.status
                                )}
                            </span>

                            <span
                                class="badge ${levelClass(
                                    caseItem.priority
                                )}"
                            >
                                Priority:
                                ${escapeHtml(
                                    caseItem.priority
                                )}
                            </span>

                            <span
                                class="badge ${levelClass(
                                    caseItem.risk_level
                                )}"
                            >
                                Risk:
                                ${escapeHtml(
                                    caseItem.risk_level
                                )}
                            </span>

                            <span
                                class="badge review-badge review-${review.key}"
                            >
                                ${escapeHtml(
                                    review.label
                                )}
                            </span>
                        </div>
                    </div>

                    <p class="case-card-summary">
                        ${escapeHtml(caseItem.summary)}
                    </p>

                    <div class="case-meta">
                        <span>
                            Opened:
                            ${formatDate(
                                caseItem.opened_date
                            )}
                        </span>

                        <span>
                            Next review:
                            ${formatDate(
                                caseItem.next_review_date
                            )}
                        </span>

                        <span>
                            Record ID: ${caseItem.id}
                        </span>

                        <span>
                            Analyst:
                            ${escapeHtml(
                                caseItem.assigned_analyst ||
                                "Unassigned"
                            )}
                        </span>

                        <span>
                            Team:
                            ${escapeHtml(
                                caseItem.responsible_team ||
                                "Unassigned"
                            )}
                        </span>
                    </div>

                    <div class="case-actions">
                        <button
                            class="small-button"
                            type="button"
                            data-action="analyze"
                            data-case-id="${caseItem.id}"
                        >
                            Analyze
                        </button>

                        ${editActions}

                        <a
                            class="small-button"
                            href="/cases/${caseItem.id}/report"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View Report
                        </a>

                        ${deleteAction}
                    </div>
                </article>
            `;
        })
        .join("");
}

function renderSelectedCase() {
    const caseItem = state.selectedCase;

    if (!caseItem) {
        elements.analysisWorkspace.classList.add(
            "hidden"
        );

        return;
    }

    const indicators = caseItem.indicators || [];
    const assessments = caseItem.assessments || [];

    const mitigations =
        caseItem.mitigation_actions || [];
    const reviews = caseItem.reviews || [];

    elements.selectedCaseTitle.textContent =
        `${caseItem.case_number}: ${caseItem.title}`;

    elements.selectedCaseSummary.innerHTML = `
        <div class="selected-case-overview">
            <div class="badge-group">
                <span class="badge">
                    ${escapeHtml(caseItem.status)}
                </span>

                <span
                    class="badge ${levelClass(
                        caseItem.priority
                    )}"
                >
                    Priority:
                    ${escapeHtml(caseItem.priority)}
                </span>

                <span
                    class="badge ${levelClass(
                        caseItem.risk_level
                    )}"
                >
                    Current Risk:
                    ${escapeHtml(
                        caseItem.risk_level
                    )}
                </span>
            </div>

            <p>
                ${escapeHtml(caseItem.summary)}
            </p>

            <div class="case-meta">
                <span>
                    Opened:
                    ${formatDate(
                        caseItem.opened_date
                    )}
                </span>

                <span>
    Next review:
    ${formatDate(
        caseItem.next_review_date
    )}
</span>

<span>
    Assigned analyst:
    ${escapeHtml(
        caseItem.assigned_analyst ||
        "Unassigned"
    )}
</span>

<span>
    Responsible team:
    ${escapeHtml(
        caseItem.responsible_team ||
        "Unassigned"
    )}
</span>

<span>
    Assigned:
    ${caseItem.assigned_at
        ? formatDateTime(
            caseItem.assigned_at
        )
        : "Not assigned"}
</span>

<span>
    Indicators: ${indicators.length}
</span>

                <span>
                    Assessments: ${assessments.length}
                </span>

                <span>
                    Mitigations: ${mitigations.length}
                    <span>
                        Reviews: ${reviews.length}
                    </span>
                </span>
            </div>
        </div>
    `;

renderIndicators(indicators);
renderAssessments(assessments);
renderMitigations(mitigations);
renderReviews(reviews);

    renderActivities(
        caseItem.activities || []
    );

    elements.analysisWorkspace.classList.remove(
        "hidden"
    );
}


function renderIndicators(indicators) {
    if (!indicators.length) {
        elements.indicatorList.innerHTML = `
            <p class="empty-state">
                No indicators recorded.
            </p>
        `;

        return;
    }

    elements.indicatorList.innerHTML =
        indicators
            .map((indicator) => `
                <article class="analysis-item">
                    <div class="analysis-item-header">
                        <div>
                            <h3>
                                ${escapeHtml(
                                    indicator.indicator_type
                                )}
                            </h3>

                            <span
                                class="badge ${levelClass(
                                    indicator.credibility
                                )}"
                            >
                                ${escapeHtml(
                                    indicator.credibility
                                )}
                            </span>
                        </div>

                        ${
    canDeleteRecords()
        ? `
            <button
                class="danger-button"
                type="button"
                data-action="delete-indicator"
                data-indicator-id="${indicator.id}"
            >
                Delete
            </button>
        `
        : ""
}
                    </div>

                    <p>
                        ${escapeHtml(
                            indicator.description
                        )}
                    </p>

                    <div class="analysis-meta">
                        <span>
                            Observed:
                            ${formatDate(
                                indicator.observed_date
                            )}
                        </span>

                        <span>
                            Source:
                            ${escapeHtml(
                                indicator.source ||
                                    "Not recorded"
                            )}
                        </span>

                        <span>
                            ID: ${indicator.id}
                        </span>
                    </div>
                </article>
            `)
            .join("");
}


function renderAssessments(assessments) {
    if (!assessments.length) {
        elements.assessmentList.innerHTML = `
            <p class="empty-state">
                No assessments recorded.
            </p>
        `;

        return;
    }

    elements.assessmentList.innerHTML =
        assessments
            .map((assessment) => `
                <article class="analysis-item">
                    <div class="analysis-item-header">
                        <div>
                            <h3>
                                Risk Assessment
                                ${formatDate(
                                    assessment.assessment_date
                                )}
                            </h3>

                            <span
                                class="badge ${levelClass(
                                    assessment.overall_risk
                                )}"
                            >
                                Overall:
                                ${escapeHtml(
                                    assessment.overall_risk
                                )}
                            </span>
                        </div>

                        ${
    canDeleteRecords()
        ? `
            <button
                class="danger-button"
                type="button"
                data-action="delete-assessment"
                data-assessment-id="${assessment.id}"
            >
                Delete
            </button>
        `
        : ""
}
                    </div>

                    <div class="assessment-levels">
                        <div class="assessment-level">
                            Threat

                            <strong>
                                ${escapeHtml(
                                    assessment.threat_level
                                )}
                            </strong>
                        </div>

                        <div class="assessment-level">
                            Vulnerability

                            <strong>
                                ${escapeHtml(
                                    assessment.vulnerability_level
                                )}
                            </strong>
                        </div>

                        <div class="assessment-level">
                            Impact

                            <strong>
                                ${escapeHtml(
                                    assessment.impact_level
                                )}
                            </strong>
                        </div>

                        <div class="assessment-level">
                            Overall Risk

                            <strong>
                                ${escapeHtml(
                                    assessment.overall_risk
                                )}
                            </strong>
                        </div>
                    </div>

                    <p>
                        <strong>Rationale:</strong>
                        <br>

                        ${escapeHtml(
                            assessment.rationale
                        )}
                    </p>

                    ${
                        assessment.recommended_action
                            ? `
                                <p>
                                    <strong>
                                        Recommended action:
                                    </strong>
                                    <br>

                                    ${escapeHtml(
                                        assessment.recommended_action
                                    )}
                                </p>
                            `
                            : ""
                    }

                    <div class="analysis-meta">
                        <span>
                            Assessed by:
                            ${escapeHtml(
                                assessment.assessed_by ||
                                    "Not recorded"
                            )}
                        </span>

                        <span>
                            ID: ${assessment.id}
                        </span>
                    </div>
                </article>
            `)
            .join("");
}
function renderMitigations(mitigations) {
    if (!mitigations.length) {
        elements.mitigationList.innerHTML = `
            <p class="empty-state">
                No mitigation actions recorded.
            </p>
        `;

        return;
    }

    elements.mitigationList.innerHTML =
        mitigations
            .map((mitigation) => {
                const canComplete =
                    mitigation.status !== "Completed";

                const deadline =
                    mitigationDeadlineStatus(
                        mitigation
                    );

                return `
                    <article
                        class="analysis-item mitigation-${deadline.key}"
                    >
                        <div
                            class="analysis-item-header"
                        >
                            <div>
                                <h3>
                                    ${escapeHtml(
                                        mitigation.title
                                    )}
                                </h3>

                                <div
                                    class="badge-group"
                                >
                                    <span
                                        class="badge ${levelClass(
                                            mitigation.priority
                                        )}"
                                    >
                                        Priority:
                                        ${escapeHtml(
                                            mitigation.priority
                                        )}
                                    </span>

                                    <span
                                        class="badge ${levelClass(
                                            mitigation.status
                                        )}"
                                    >
                                        ${escapeHtml(
                                            mitigation.status
                                        )}
                                    </span>

                                    <span
                                        class="badge mitigation-deadline-badge mitigation-${deadline.key}"
                                    >
                                        ${escapeHtml(
                                            deadline.label
                                        )}
                                    </span>
                                </div>
                            </div>

                            <div
                                <div
    class="mitigation-actions"
>
    ${
        canEditCases() && canComplete
            ? `
                <button
                    class="small-button"
                    type="button"
                    data-action="complete-mitigation"
                    data-mitigation-id="${mitigation.id}"
                >
                    Mark Completed
                </button>
            `
            : ""
    }

    ${
        canDeleteRecords()
            ? `
                <button
                    class="danger-button"
                    type="button"
                    data-action="delete-mitigation"
                    data-mitigation-id="${mitigation.id}"
                >
                    Delete
                </button>
            `
            : ""
    }
</div>
                            </div>
                        </div>

                        <p>
                            ${escapeHtml(
                                mitigation.description
                            )}
                        </p>

                        <div class="analysis-meta">
                            <span>
                                Owner:
                                ${escapeHtml(
                                    mitigation.owner ||
                                        "Unassigned"
                                )}
                            </span>

                            <span>
                                Due:
                                ${formatDate(
                                    mitigation.due_date
                                )}
                            </span>

                            <span>
                                Completed:
                                ${
                                    mitigation.completed_date
                                        ? formatDate(
                                            mitigation.completed_date
                                        )
                                        : "Not completed"
                                }
                            </span>

                            <span>
                                ID: ${mitigation.id}
                            </span>
                        </div>
                    </article>
                `;
            })
            .join("");
}

function renderReviews(reviews) {
    if (!reviews.length) {
        elements.reviewList.innerHTML = `
            <p class="empty-state">
                No case reviews recorded.
            </p>
        `;

        return;
    }

    elements.reviewList.innerHTML =
        reviews
            .map((review) => `
                <article class="analysis-item">
                    <div class="analysis-item-header">
                        <div>
                            <h3>
                                Case Review
                                ${formatDate(
                                    review.review_date
                                )}
                            </h3>

                            <span class="badge green">
                                Completed
                            </span>
                        </div>
                    </div>

                    <p>
                        <strong>Findings:</strong>
                        <br>

                        ${escapeHtml(
                            review.findings
                        )}
                    </p>

                    <div class="analysis-meta">
                        <span>
                            Reviewed by:
                            ${escapeHtml(
                                review.reviewed_by
                            )}
                        </span>

                        <span>
                            Next review:
                            ${formatDate(
                                review.next_review_date
                            )}
                        </span>

                        <span>
                            Recorded:
                            ${formatDateTime(
                                review.created_at
                            )}
                        </span>

                        <span>
                            ID: ${review.id}
                        </span>
                    </div>
                </article>
            `)
            .join("");
}
function activityLabel(activityType) {
    const labels = {
        case_created: "Case Created",
        case_updated: "Case Updated",
        case_archived: "Case Archived",
        case_restored: "Case Restored",
        case_reviewed: "Case Reviewed",
        indicator_created: "Indicator Added",
        indicator_deleted: "Indicator Deleted",
        assessment_created: "Assessment Recorded",
        assessment_deleted: "Assessment Deleted",
        mitigation_created: "Mitigation Created",
        mitigation_updated: "Mitigation Updated",
        mitigation_deleted: "Mitigation Deleted",
    };

    return (
        labels[activityType] ||
        activityType
            .split("_")
            .map(
                (word) =>
                    word.charAt(0).toUpperCase() +
                    word.slice(1)
            )
            .join(" ")
    );
}


function activityCategory(activityType) {
    if (
        activityType.startsWith("indicator_")
    ) {
        return "indicator";
    }

    if (
        activityType.startsWith("assessment_")
    ) {
        return "assessment";
    }

    if (
        activityType.startsWith("mitigation_")
    ) {
        return "mitigation";
    }

    return "case";
}


function renderActivities(activities) {
    if (!activities.length) {
        elements.activityList.innerHTML = `
            <p class="empty-state">
                No case activity recorded.
            </p>
        `;

        return;
    }

    elements.activityList.innerHTML =
        activities
            .map((activity) => `
                <article class="activity-item">
                    <span
                        class="activity-marker ${activityCategory(
                            activity.activity_type
                        )}"
                        aria-hidden="true"
                    ></span>

                    <div class="activity-content">
                        <div class="activity-header">
                            <h3
                                class="activity-type"
                            >
                                ${escapeHtml(
                                    activityLabel(
                                        activity.activity_type
                                    )
                                )}
                            </h3>

                            <time
                                class="activity-time"
                            >
                                ${escapeHtml(
                                    formatDateTime(
                                        activity.created_at
                                    )
                                )}
                            </time>
                        </div>

                        <p
                            class="activity-description"
                        >
                            ${escapeHtml(
                                activity.description
                            )}
                        </p>

                        <p class="activity-actor">
                            Recorded by:
                            ${escapeHtml(
                                activity.actor ||
                                    "System"
                            )}
                        </p>
                    </div>
                </article>
            `)
            .join("");
}


async function loadCases() {
    try {
        state.cases = await apiRequest(
            "/cases?include_archived=true"
        );

        updateStatistics();
        renderCases();

        if (state.selectedCaseId !== null) {
            const selectedStillExists =
                state.cases.some(
                    (caseItem) =>
                        caseItem.id ===
                        state.selectedCaseId
                );

            if (selectedStillExists) {
                await loadSelectedCase(
                    state.selectedCaseId,
                    false
                );
            } else {
                closeAnalysisWorkspace();
            }
        }
    } catch (error) {
        elements.caseList.innerHTML = `
            <p class="empty-state error-state">
                ${escapeHtml(error.message)}
            </p>
        `;

        showToast(error.message, true);
    }
}


async function loadSelectedCase(
    caseId,
    scrollToWorkspace = true
) {
    try {
        state.selectedCaseId = Number(caseId);

state.selectedCase = await apiRequest(
    `/cases/${state.selectedCaseId}`
);

elements.reviewForm.reset();

elements.reviewDate.value =
    today();

elements.reviewedBy.value =
    state.selectedCase.assigned_analyst || "";

renderCases();
renderSelectedCase();

        if (scrollToWorkspace) {
            elements.analysisWorkspace
                .scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
        }
    } catch (error) {
        showToast(error.message, true);
    }
}


function closeAnalysisWorkspace() {
    state.selectedCaseId = null;
    state.selectedCase = null;

    elements.analysisWorkspace.classList.add(
        "hidden"
    );

    renderCases();
}


function resetCaseForm() {
    elements.caseForm.reset();
    elements.editingCaseId.value = "";

    elements.caseFormTitle.textContent =
        "Create New Case";

    elements.cancelEditButton.classList.add(
        "hidden"
    );

    elements.caseStatus.value = "Open";
    elements.casePriority.value = "Routine";

    elements.caseRiskLevel.value =
        "Undetermined";

    elements.openedDate.value = today();
}


function beginCaseEdit(caseId) {
    const caseItem = state.cases.find(
        (item) => item.id === Number(caseId)
    );

    if (!caseItem) {
        showToast(
            "The selected case could not be found.",
            true
        );

        return;
    }

    if (caseItem.is_archived) {
        showToast(
            "Restore this case before editing it.",
            true
        );

        return;
    }

    elements.editingCaseId.value =
        caseItem.id;

    elements.caseFormTitle.textContent =
        `Edit ${caseItem.case_number}`;

    elements.caseNumber.value =
        caseItem.case_number;

    elements.caseTitle.value =
        caseItem.title;

    elements.caseSummary.value =
        caseItem.summary;

    elements.caseStatus.value =
        caseItem.status;

    elements.casePriority.value =
        caseItem.priority;

    elements.caseRiskLevel.value =
        caseItem.risk_level;

    elements.openedDate.value =
        caseItem.opened_date;

    elements.nextReviewDate.value =
    caseItem.next_review_date || "";

elements.assignedAnalyst.value =
    caseItem.assigned_analyst || "";

elements.responsibleTeam.value =
    caseItem.responsible_team || "";

elements.cancelEditButton.classList.remove(
        "hidden"
    );

    elements.caseForm.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


async function saveCase(event) {
    event.preventDefault();

    const editingCaseId =
        elements.editingCaseId.value;

    const payload = {
        case_number:
            elements.caseNumber.value.trim(),

        title:
            elements.caseTitle.value.trim(),

        summary:
            elements.caseSummary.value.trim(),

        status:
            elements.caseStatus.value,

        priority:
            elements.casePriority.value,

        risk_level:
            elements.caseRiskLevel.value,

        opened_date:
            elements.openedDate.value,

        next_review_date:
    elements.nextReviewDate.value ||
    null,

assigned_analyst:
    elements.assignedAnalyst.value.trim() ||
    null,

responsible_team:
    elements.responsibleTeam.value.trim() ||
    null,
    };

    try {
        if (editingCaseId) {
            await apiRequest(
                `/cases/${editingCaseId}`,
                {
                    method: "PATCH",
                    body: JSON.stringify(payload),
                }
            );

            showToast(
                "Case updated successfully."
            );
        } else {
            await apiRequest("/cases", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            showToast(
                "Case created successfully."
            );
        }

        resetCaseForm();
        await loadCases();
    } catch (error) {
        showToast(error.message, true);
    }
}


async function deleteCase(caseId) {
    const caseItem = state.cases.find(
        (item) => item.id === Number(caseId)
    );

    const confirmed = window.confirm(
        `Delete ${
            caseItem?.case_number ||
            "this case"
        } and all associated intelligence records?`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${caseId}`,
            {
                method: "DELETE",
            }
        );

        if (
            state.selectedCaseId ===
            Number(caseId)
        ) {
            closeAnalysisWorkspace();
        }

        resetCaseForm();
        await loadCases();

        showToast("Case deleted.");
    } catch (error) {
        showToast(error.message, true);
    }
}


async function archiveCase(caseId) {
    const caseItem = state.cases.find(
        (item) => item.id === Number(caseId)
    );

    const confirmed = window.confirm(
        `Archive ${
            caseItem?.case_number ||
            "this case"
        }? It will be removed from the active register.`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${caseId}/archive`,
            {
                method: "PATCH",
            }
        );

        if (
            state.selectedCaseId ===
            Number(caseId)
        ) {
            closeAnalysisWorkspace();
        }

        if (
            elements.editingCaseId.value ===
            String(caseId)
        ) {
            resetCaseForm();
        }

        await loadCases();
        showToast("Case archived.");
    } catch (error) {
        showToast(error.message, true);
    }
}


async function restoreCase(caseId) {
    try {
        await apiRequest(
            `/cases/${caseId}/restore`,
            {
                method: "PATCH",
            }
        );

        await loadCases();

        showToast(
            "Case restored to the active register."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}
async function saveReview(event) {
    event.preventDefault();

    if (state.selectedCaseId === null) {
        showToast(
            "Select a case first.",
            true
        );

        return;
    }

    const payload = {
        review_date:
            elements.reviewDate.value,

        reviewed_by:
            elements.reviewedBy
                .value
                .trim(),

        findings:
            elements.reviewFindings
                .value
                .trim(),

        next_review_date:
            elements.reviewNextDate.value ||
            null,
    };

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/reviews`,
            {
                method: "POST",
                body: JSON.stringify(payload),
            }
        );

        await loadCases();

        elements.reviewForm.reset();

        elements.reviewDate.value =
            today();

        elements.reviewedBy.value =
            state.selectedCase
                ?.assigned_analyst || "";

        showToast(
            "Case review recorded."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}
async function saveIndicator(event) {
    event.preventDefault();

    if (state.selectedCaseId === null) {
        showToast(
            "Select a case first.",
            true
        );

        return;
    }

    const payload = {
        indicator_type:
            elements.indicatorType.value,

        description:
            elements.indicatorDescription
                .value
                .trim(),

        source:
            elements.indicatorSource
                .value
                .trim() ||
            null,

        credibility:
            elements.indicatorCredibility.value,

        observed_date:
            elements.indicatorObservedDate.value,
    };

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/indicators`,
            {
                method: "POST",
                body: JSON.stringify(payload),
            }
        );

        elements.indicatorForm.reset();

        elements.indicatorCredibility.value =
            "Unassessed";

        elements.indicatorObservedDate.value =
            today();

        await loadCases();

        showToast("Indicator added.");
    } catch (error) {
        showToast(error.message, true);
    }
}


async function deleteIndicator(
    indicatorId
) {
    if (state.selectedCaseId === null) {
        return;
    }

    if (
        !window.confirm(
            "Delete this indicator?"
        )
    ) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/indicators/${indicatorId}`,
            {
                method: "DELETE",
            }
        );

        await loadCases();

        showToast("Indicator deleted.");
    } catch (error) {
        showToast(error.message, true);
    }
}


async function saveAssessment(event) {
    event.preventDefault();

    if (state.selectedCaseId === null) {
        showToast(
            "Select a case first.",
            true
        );

        return;
    }

    const payload = {
        threat_level:
            elements.threatLevel.value,

        vulnerability_level:
            elements.vulnerabilityLevel.value,

        impact_level:
            elements.impactLevel.value,

        overall_risk:
            elements.overallRisk.value,

        rationale:
            elements.assessmentRationale
                .value
                .trim(),

        recommended_action:
            elements.recommendedAction
                .value
                .trim() ||
            null,

        assessed_by:
            elements.assessedBy
                .value
                .trim() ||
            null,

        assessment_date:
            elements.assessmentDate.value,
    };

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/assessments`,
            {
                method: "POST",
                body: JSON.stringify(payload),
            }
        );

        elements.assessmentForm.reset();

        elements.threatLevel.value = "Low";

        elements.vulnerabilityLevel.value =
            "Low";

        elements.impactLevel.value = "Low";
        elements.overallRisk.value = "Low";

        elements.assessmentDate.value =
            today();

        await loadCases();

        showToast(
            "Risk assessment recorded."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}


async function deleteAssessment(
    assessmentId
) {
    if (state.selectedCaseId === null) {
        return;
    }

    if (
        !window.confirm(
            "Delete this risk assessment?"
        )
    ) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/assessments/${assessmentId}`,
            {
                method: "DELETE",
            }
        );

        await loadCases();

        showToast(
            "Risk assessment deleted."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}


async function saveMitigation(event) {
    event.preventDefault();

    if (state.selectedCaseId === null) {
        showToast(
            "Select a case first.",
            true
        );

        return;
    }

    const payload = {
        title:
            elements.mitigationTitle
                .value
                .trim(),

        description:
            elements.mitigationDescription
                .value
                .trim(),

        owner:
            elements.mitigationOwner
                .value
                .trim() ||
            null,

        priority:
            elements.mitigationPriority.value,

        status:
            elements.mitigationStatus.value,

        due_date:
            elements.mitigationDueDate.value ||
            null,

        completed_date: null,
    };

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/mitigations`,
            {
                method: "POST",
                body: JSON.stringify(payload),
            }
        );

        elements.mitigationForm.reset();

        elements.mitigationPriority.value =
            "Moderate";

        elements.mitigationStatus.value =
            "Planned";

        await loadCases();

        showToast(
            "Mitigation action added."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}


async function completeMitigation(
    mitigationId
) {
    if (state.selectedCaseId === null) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/mitigations/${mitigationId}`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    status: "Completed",
                }),
            }
        );

        await loadCases();

        showToast(
            "Mitigation action completed."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}


async function deleteMitigation(
    mitigationId
) {
    if (state.selectedCaseId === null) {
        return;
    }

    if (
        !window.confirm(
            "Delete this mitigation action?"
        )
    ) {
        return;
    }

    try {
        await apiRequest(
            `/cases/${state.selectedCaseId}/mitigations/${mitigationId}`,
            {
                method: "DELETE",
            }
        );

        await loadCases();

        showToast(
            "Mitigation action deleted."
        );
    } catch (error) {
        showToast(error.message, true);
    }
}

elements.loginForm.addEventListener(
    "submit",
    submitLogin
);


elements.bootstrapForm.addEventListener(
    "submit",
    submitBootstrap
);


elements.showBootstrapButton.addEventListener(
    "click",
    showBootstrapPanel
);


elements.showLoginButton.addEventListener(
    "click",
    showLoginPanel
);


elements.logoutButton.addEventListener(
    "click",
    logout
);



elements.caseForm.addEventListener(
    "submit",
    saveCase
);


elements.cancelEditButton.addEventListener(
    "click",
    resetCaseForm
);


elements.refreshButton.addEventListener(
    "click",
    async () => {
        await loadCases();

        showToast(
            "Case register refreshed."
        );
    }
);


elements.searchInput.addEventListener(
    "input",
    renderCases
);


elements.statusFilter.addEventListener(
    "change",
    renderCases
);

elements.reviewFilter.addEventListener(
    "change",
    renderCases
);

elements.archiveFilter.addEventListener(
    "change",
    () => {
        updateCaseRegisterTitle();
        renderCases();

        if (state.selectedCase) {
            const archiveView =
                elements.archiveFilter.value;

            const selectedIsVisible =
                archiveView === "all" ||
                (
                    archiveView ===
                        "archived" &&
                    state.selectedCase
                        .is_archived
                ) ||
                (
                    archiveView === "active" &&
                    !state.selectedCase
                        .is_archived
                );

            if (!selectedIsVisible) {
                closeAnalysisWorkspace();
            }
        }
    }
);

elements.analystFilter.addEventListener(
    "input",
    renderCases
);


elements.teamFilter.addEventListener(
    "input",
    renderCases
);

createSortControl();


elements.sortSelect.addEventListener(
    "change",
    () => {
        state.sortBy =
            elements.sortSelect.value;

        renderCases();
    }
);


elements.closeWorkspaceButton.addEventListener(
    "click",
    closeAnalysisWorkspace
);


elements.indicatorForm.addEventListener(
    "submit",
    saveIndicator
);


elements.assessmentForm.addEventListener(
    "submit",
    saveAssessment
);


elements.mitigationForm.addEventListener(
    "submit",
    saveMitigation
);
elements.reviewForm.addEventListener(
    "submit",
    saveReview
);


elements.caseList.addEventListener(
    "click",
    async (event) => {
        const button = event.target.closest(
            "button[data-action]"
        );

        if (!button) {
            return;
        }

        const action =
            button.dataset.action;

        const caseId = Number(
            button.dataset.caseId
        );

        if (action === "analyze") {
            await loadSelectedCase(caseId);
        }

        if (action === "edit") {
            beginCaseEdit(caseId);
        }

        if (action === "archive-case") {
            await archiveCase(caseId);
        }

        if (action === "restore-case") {
            await restoreCase(caseId);
        }

        if (action === "delete-case") {
            await deleteCase(caseId);
        }
    }
);


elements.indicatorList.addEventListener(
    "click",
    async (event) => {
        const button = event.target.closest(
            'button[data-action="delete-indicator"]'
        );

        if (!button) {
            return;
        }

        await deleteIndicator(
            Number(
                button.dataset.indicatorId
            )
        );
    }
);


elements.assessmentList.addEventListener(
    "click",
    async (event) => {
        const button = event.target.closest(
            'button[data-action="delete-assessment"]'
        );

        if (!button) {
            return;
        }

        await deleteAssessment(
            Number(
                button.dataset.assessmentId
            )
        );
    }
);


elements.mitigationList.addEventListener(
    "click",
    async (event) => {
        const button = event.target.closest(
            "button[data-action]"
        );

        if (!button) {
            return;
        }

        const mitigationId = Number(
            button.dataset.mitigationId
        );

        if (
            button.dataset.action ===
            "complete-mitigation"
        ) {
            await completeMitigation(
                mitigationId
            );
        }

        if (
            button.dataset.action ===
            "delete-mitigation"
        ) {
            await deleteMitigation(
                mitigationId
            );
        }
    }
);


resetCaseForm();
updateCaseRegisterTitle();

elements.indicatorObservedDate.value =
    today();

elements.assessmentDate.value =
    today();

elements.reviewDate.value =
    today();

initializeApplication();
