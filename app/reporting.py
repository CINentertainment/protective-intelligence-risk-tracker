from datetime import date, datetime
from html import escape

from app import models


def safe(value: object | None) -> str:
    if value is None or value == "":
        return "Not recorded"

    return escape(str(value))


def format_date(value: date | None) -> str:
    if value is None:
        return "Not scheduled"

    return value.strftime("%m/%d/%Y")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "Unknown time"

    return value.strftime("%m/%d/%Y %I:%M %p")


def badge(value: str, category: str = "") -> str:
    css_class = f"badge {category}".strip()

    return (
        f'<span class="{css_class}">'
        f"{safe(value)}"
        f"</span>"
    )


def render_indicators(case: models.Case) -> str:
    if not case.indicators:
        return '<p class="empty">No indicators recorded.</p>'

    items = []

    for indicator in case.indicators:
        items.append(
            f"""
            <article class="record">
                <div class="record-heading">
                    <h3>{safe(indicator.indicator_type)}</h3>
                    {badge(indicator.credibility)}
                </div>

                <p>{safe(indicator.description)}</p>

                <div class="metadata">
                    <span>
                        <strong>Observed:</strong>
                        {format_date(indicator.observed_date)}
                    </span>

                    <span>
                        <strong>Source:</strong>
                        {safe(indicator.source)}
                    </span>
                </div>
            </article>
            """
        )

    return "".join(items)


def render_assessments(case: models.Case) -> str:
    if not case.assessments:
        return '<p class="empty">No assessments recorded.</p>'

    items = []

    for assessment in case.assessments:
        items.append(
            f"""
            <article class="record">
                <div class="record-heading">
                    <h3>
                        Assessment —
                        {format_date(assessment.assessment_date)}
                    </h3>

                    {badge(
                        assessment.overall_risk,
                        assessment.overall_risk.lower(),
                    )}
                </div>

                <div class="assessment-grid">
                    <div>
                        <span>Threat</span>
                        <strong>
                            {safe(assessment.threat_level)}
                        </strong>
                    </div>

                    <div>
                        <span>Vulnerability</span>
                        <strong>
                            {safe(assessment.vulnerability_level)}
                        </strong>
                    </div>

                    <div>
                        <span>Impact</span>
                        <strong>
                            {safe(assessment.impact_level)}
                        </strong>
                    </div>

                    <div>
                        <span>Overall Risk</span>
                        <strong>
                            {safe(assessment.overall_risk)}
                        </strong>
                    </div>
                </div>

                <p>
                    <strong>Analytic rationale:</strong><br>
                    {safe(assessment.rationale)}
                </p>

                <p>
                    <strong>Recommended action:</strong><br>
                    {safe(assessment.recommended_action)}
                </p>

                <p class="small">
                    Assessed by:
                    {safe(assessment.assessed_by)}
                </p>
            </article>
            """
        )

    return "".join(items)


def render_mitigations(case: models.Case) -> str:
    if not case.mitigation_actions:
        return (
            '<p class="empty">'
            "No mitigation actions recorded."
            "</p>"
        )

    items = []

    for mitigation in case.mitigation_actions:
        items.append(
            f"""
            <article class="record">
                <div class="record-heading">
                    <h3>{safe(mitigation.title)}</h3>

                    <div>
                        {badge(mitigation.priority)}
                        {badge(mitigation.status)}
                    </div>
                </div>

                <p>{safe(mitigation.description)}</p>

                <div class="metadata">
                    <span>
                        <strong>Owner:</strong>
                        {safe(mitigation.owner)}
                    </span>

                    <span>
                        <strong>Due:</strong>
                        {format_date(mitigation.due_date)}
                    </span>

                    <span>
                        <strong>Completed:</strong>
                        {format_date(mitigation.completed_date)}
                    </span>
                </div>
            </article>
            """
        )

    return "".join(items)


def render_activities(case: models.Case) -> str:
    if not case.activities:
        return '<p class="empty">No activity recorded.</p>'

    items = []

    for activity in case.activities:
        activity_name = activity.activity_type.replace(
            "_",
            " ",
        ).title()

        items.append(
            f"""
            <article class="timeline-item">
                <div class="timeline-marker"></div>

                <div>
                    <div class="record-heading">
                        <h3>{safe(activity_name)}</h3>

                        <time>
                            {format_datetime(activity.created_at)}
                        </time>
                    </div>

                    <p>{safe(activity.description)}</p>

                    <p class="small">
                        Recorded by:
                        {safe(activity.actor or "System")}
                    </p>
                </div>
            </article>
            """
        )

    return "".join(items)


def build_case_report(case: models.Case) -> str:
    generated_at = datetime.now()

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>
            {safe(case.case_number)} Intelligence Report
        </title>

        <style>
            :root {{
                --navy: #071727;
                --blue: #16324c;
                --cyan: #138eaa;
                --light: #eef5f8;
                --border: #b8c7d1;
                --text: #17232d;
                --muted: #526574;
                --amber: #b87900;
                --red: #b42336;
                --green: #18734b;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                background: #dfe7ec;
                color: var(--text);
                font-family: Arial, Helvetica, sans-serif;
                line-height: 1.45;
            }}

            .toolbar {{
                position: sticky;
                top: 0;
                z-index: 10;
                display: flex;
                justify-content: center;
                gap: 10px;
                padding: 12px;
                background: var(--navy);
            }}

            .toolbar button {{
                padding: 9px 16px;
                border: 1px solid #4c718c;
                border-radius: 5px;
                background: #12314a;
                color: white;
                font-weight: 700;
                cursor: pointer;
            }}

            .toolbar button.primary {{
                border-color: var(--cyan);
                background: var(--cyan);
            }}

            .report {{
                width: min(920px, calc(100% - 30px));
                margin: 24px auto;
                background: white;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
            }}

            .report-header {{
                padding: 34px 42px;
                background: var(--navy);
                color: white;
            }}

            .organization {{
                margin: 0 0 8px;
                color: #54d4ef;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.16em;
            }}

            h1 {{
                margin: 0 0 7px;
                font-size: 2rem;
            }}

            .subtitle {{
                margin: 0;
                color: #bed1df;
            }}

            .report-body {{
                padding: 34px 42px 48px;
            }}

            .classification {{
                margin-bottom: 24px;
                padding: 8px;
                border: 1px solid var(--border);
                text-align: center;
                font-size: 0.75rem;
                font-weight: 800;
                letter-spacing: 0.12em;
            }}

            section {{
                margin-top: 34px;
                break-inside: avoid;
            }}

            section > h2 {{
                margin: 0 0 15px;
                padding-bottom: 8px;
                border-bottom: 2px solid var(--cyan);
                color: var(--blue);
                font-size: 1.15rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }}

            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px;
            }}

            .summary-field {{
                padding: 12px;
                border: 1px solid var(--border);
                background: var(--light);
            }}

            .summary-field.full {{
                grid-column: 1 / -1;
            }}

            .summary-field span {{
                display: block;
                margin-bottom: 5px;
                color: var(--muted);
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
            }}

            .record {{
                margin-bottom: 13px;
                padding: 17px;
                border: 1px solid var(--border);
                border-left: 4px solid var(--cyan);
                break-inside: avoid;
            }}

            .record-heading {{
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 18px;
            }}

            .record h3,
            .timeline-item h3 {{
                margin: 0 0 8px;
                font-size: 1rem;
            }}

            .badge {{
                display: inline-block;
                margin-left: 4px;
                padding: 4px 8px;
                border: 1px solid var(--border);
                border-radius: 999px;
                color: var(--blue);
                font-size: 0.7rem;
                font-weight: 800;
            }}

            .badge.high,
            .badge.critical {{
                border-color: var(--red);
                color: var(--red);
            }}

            .badge.moderate {{
                border-color: var(--amber);
                color: var(--amber);
            }}

            .badge.low {{
                border-color: var(--green);
                color: var(--green);
            }}

            .metadata {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px 22px;
                color: var(--muted);
                font-size: 0.78rem;
            }}

            .assessment-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
                margin: 14px 0;
            }}

            .assessment-grid div {{
                padding: 10px;
                border: 1px solid var(--border);
                background: var(--light);
                text-align: center;
            }}

            .assessment-grid span {{
                display: block;
                color: var(--muted);
                font-size: 0.68rem;
                text-transform: uppercase;
            }}

            .timeline {{
                position: relative;
                padding-left: 24px;
            }}

            .timeline::before {{
                content: "";
                position: absolute;
                top: 7px;
                bottom: 7px;
                left: 5px;
                width: 2px;
                background: var(--cyan);
            }}

            .timeline-item {{
                position: relative;
                padding: 0 0 20px 15px;
                break-inside: avoid;
            }}

            .timeline-marker {{
                position: absolute;
                top: 5px;
                left: -24px;
                width: 11px;
                height: 11px;
                border-radius: 50%;
                background: var(--cyan);
            }}

            .timeline-item p {{
                margin: 4px 0;
            }}

            .timeline-item time {{
                color: var(--muted);
                font-size: 0.75rem;
            }}

            .small,
            .empty {{
                color: var(--muted);
                font-size: 0.78rem;
            }}

            .report-footer {{
                padding: 17px 42px;
                border-top: 1px solid var(--border);
                color: var(--muted);
                font-size: 0.72rem;
                text-align: center;
            }}

            @media print {{
                @page {{
                    size: letter;
                    margin: 0.55in;
                }}

                body {{
                    background: white;
                }}

                .toolbar {{
                    display: none;
                }}

                .report {{
                    width: 100%;
                    margin: 0;
                    box-shadow: none;
                }}

                .report-header {{
                    padding: 24px 28px;
                }}

                .report-body {{
                    padding: 24px 28px;
                }}

                section {{
                    margin-top: 25px;
                }}
            }}

            @media (max-width: 650px) {{
                .report-header,
                .report-body {{
                    padding: 24px;
                }}

                .summary-grid,
                .assessment-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="toolbar">
            <button
                type="button"
                onclick="window.history.back()"
            >
                Back to Dashboard
            </button>

            <button
                class="primary"
                type="button"
                onclick="window.print()"
            >
                Print / Save as PDF
            </button>
        </div>

        <main class="report">
            <header class="report-header">
                <p class="organization">CIN ENTERTAINMENT</p>

                <h1>Protective Intelligence Case Report</h1>

                <p class="subtitle">
                    {safe(case.case_number)} ·
                    Generated {format_datetime(generated_at)}
                </p>
            </header>

            <div class="report-body">
                <div class="classification">
                    UNCLASSIFIED // FOR OFFICIAL USE
                </div>

                <section>
                    <h2>Case Overview</h2>

                    <div class="summary-grid">
                        <div class="summary-field">
                            <span>Case Number</span>
                            <strong>
                                {safe(case.case_number)}
                            </strong>
                        </div>

                        <div class="summary-field">
                            <span>Title</span>
                            <strong>{safe(case.title)}</strong>
                        </div>

                        <div class="summary-field">
                            <span>Status</span>
                            <strong>{safe(case.status)}</strong>
                        </div>

                        <div class="summary-field">
                            <span>Priority</span>
                            <strong>{safe(case.priority)}</strong>
                        </div>

                        <div class="summary-field">
                            <span>Risk Level</span>
                            <strong>{safe(case.risk_level)}</strong>
                        </div>

                        <div class="summary-field">
                            <span>Opened</span>
                            <strong>
                                {format_date(case.opened_date)}
                            </strong>
                        </div>

                        <div class="summary-field">
                            <span>Next Review</span>
                            <strong>
                                {format_date(case.next_review_date)}
                            </strong>
                        </div>

                        <div class="summary-field">
                            <span>Last Updated</span>
                            <strong>
                                {format_datetime(case.updated_at)}
                            </strong>
                        </div>

                        <div class="summary-field full">
                            <span>Executive Summary</span>
                            <strong>{safe(case.summary)}</strong>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>Indicators</h2>
                    {render_indicators(case)}
                </section>

                <section>
                    <h2>Risk Assessments</h2>
                    {render_assessments(case)}
                </section>

                <section>
                    <h2>Mitigation Actions</h2>
                    {render_mitigations(case)}
                </section>

                <section>
                    <h2>Case Activity Timeline</h2>

                    <div class="timeline">
                        {render_activities(case)}
                    </div>
                </section>
            </div>

            <footer class="report-footer">
                Protective Intelligence Risk Tracker · Version 0.5.0
            </footer>
        </main>
    </body>
    </html>
    """