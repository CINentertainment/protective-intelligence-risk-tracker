const state = {
    cases: [],
    selectedCaseId: null,
    selectedCase: null,
    sortBy: "review-urgency",
};

const elements = {
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

    activityList: document.getElementById("activityList"),
    toast: document.getElementById("toast"),
};


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

        throw new Error(message);
    }

    return data;
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

    const selectedStatus =
        elements.statusFilter.value;

    const archiveView =
        elements.archiveFilter.value;

    return state.cases
        .filter((caseItem) => {
            const matchesStatus =
                !selectedStatus ||
                caseItem.status === selectedStatus;

            const searchableText = [
                caseItem.case_number,
                caseItem.title,
                caseItem.summary,
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

            return (
                matchesStatus &&
                matchesSearch &&
                matchesArchiveView
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

            const operationalActions =
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
                            data-action="analyze"
                            data-case-id="${caseItem.id}"
                        >
                            Analyze
                        </button>

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
                    `;

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
                    </div>

                    <div class="case-actions">
                        ${operationalActions}

                        <a
                            class="small-button"
                            href="/cases/${caseItem.id}/report"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View Report
                        </a>

                        <button
                            class="danger-button"
                            type="button"
                            data-action="delete-case"
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
                    Indicators: ${indicators.length}
                </span>

                <span>
                    Assessments: ${assessments.length}
                </span>

                <span>
                    Mitigations: ${mitigations.length}
                </span>
            </div>
        </div>
    `;

    renderIndicators(indicators);
    renderAssessments(assessments);
    renderMitigations(mitigations);

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

                        <button
                            class="danger-button"
                            type="button"
                            data-action="delete-indicator"
                            data-indicator-id="${indicator.id}"
                        >
                            Delete
                        </button>
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

                        <button
                            class="danger-button"
                            type="button"
                            data-action="delete-assessment"
                            data-assessment-id="${assessment.id}"
                        >
                            Delete
                        </button>
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
                                class="mitigation-actions"
                            >
                                ${
                                    canComplete
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

                                <button
                                    class="danger-button"
                                    type="button"
                                    data-action="delete-mitigation"
                                    data-mitigation-id="${mitigation.id}"
                                >
                                    Delete
                                </button>
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


function activityLabel(activityType) {
    const labels = {
        case_created: "Case Created",
        case_updated: "Case Updated",
        case_archived: "Case Archived",
        case_restored: "Case Restored",
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

loadCases();