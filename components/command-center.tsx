"use client";

import { useState } from "react";
import {
  activities,
  decisions,
  impactMetrics,
  permits,
  project,
} from "@/lib/permit/demo-data";
import type { PermitStatus } from "@/types/permit";

type ReviewState = "idle" | "running" | "decision" | "approved";

const statusLabels: Record<PermitStatus, string> = {
  ready: "Ready",
  review: "Review",
  missing: "Action required",
  pending: "Pending",
};

function StatusBadge({ status }: { status: PermitStatus }) {
  return (
    <span className={`status-badge status-${status}`}>
      <span className="status-dot" />
      {statusLabels[status]}
    </span>
  );
}

function Icon({
  children,
  size = 18,
}: {
  children: React.ReactNode;
  size?: number;
}) {
  return (
    <span
      aria-hidden="true"
      className="inline-icon"
      style={{ width: size, height: size }}
    >
      {children}
    </span>
  );
}

export default function CommandCenter() {
  const [reviewState, setReviewState] = useState<ReviewState>("idle");

  const startReview = () => {
    setReviewState("running");

    window.setTimeout(() => {
      setReviewState("decision");
    }, 900);
  };

  const approveDecision = () => {
    setReviewState("approved");
  };

  const running = reviewState === "running";
  const decisionVisible =
    reviewState === "decision" || reviewState === "approved";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-mark">P</div>
            <div>
              <div className="brand-name">PermitPilot</div>
              <div className="brand-subtitle">AUTONOMOUS OPERATIONS</div>
            </div>
          </div>

          <nav className="nav-list" aria-label="Primary navigation">
            <button className="nav-item nav-item-active">
              <Icon>
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M4 13h6V4H4v9Zm0 7h6v-4H4v4Zm10 0h6v-9h-6v9Zm0-16v4h6V4h-6Z" />
                </svg>
              </Icon>
              Overview
            </button>

            <button className="nav-item">
              <Icon>
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M7 3h8l4 4v14H7V3Zm8 0v5h4M10 12h6M10 16h6" />
                </svg>
              </Icon>
              Permits
              <span className="nav-count">7</span>
            </button>

            <button className="nav-item">
              <Icon>
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M4 5h16v14H4V5Zm4-2v4M16 3v4M4 9h16" />
                </svg>
              </Icon>
              Documents
              <span className="nav-count">14</span>
            </button>

            <button className="nav-item">
              <Icon>
                <svg viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />
                </svg>
              </Icon>
              Agent activity
            </button>

            <button className="nav-item">
              <Icon>
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 3 4 7v5c0 5 3.4 8 8 9 4.6-1 8-4 8-9V7l-8-4Z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </Icon>
              Audit trail
            </button>
          </nav>
        </div>

        <div className="sidebar-footer">
          <div className="runtime-status">
            <span className="runtime-dot" />
            <div>
              <strong>Agent runtime</strong>
              <span>Ready</span>
            </div>
          </div>
          <div className="sidebar-build">PermitPilot AI ï¿½ Competition Build</div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <div className="eyebrow">PROJECT / {project.id}</div>
            <h1>{project.name}</h1>
            <div className="project-meta">
              <span>{project.address}</span>
              <span className="meta-separator">ï¿½</span>
              <span>{project.projectType}</span>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="environment-pill">
              <span />
              Professional Agent
            </div>
            <button className="icon-button" aria-label="Notifications">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7M10 20h4" />
              </svg>
              <span className="notification-dot" />
            </button>
          </div>
        </header>

        <section className="goal-panel">
          <div className="goal-copy">
            <div className="section-label">
              <span className="section-label-dot" />
              AUTONOMOUS PROJECT GOAL
            </div>
            <h2>{project.goal}</h2>
            <p>
              PermitPilot will determine jurisdiction, identify requirements,
              review project documents, detect compliance risks, prepare
              application artifacts, and escalate only material decisions.
            </p>
          </div>

          <button
            className={`primary-action ${running ? "primary-action-running" : ""}`}
            onClick={startReview}
            disabled={running || reviewState === "approved"}
          >
            {running ? (
              <>
                <span className="spinner" />
                Analyzing project
              </>
            ) : reviewState === "approved" ? (
              <>
                <span className="check-icon">?</span>
                Review completed
              </>
            ) : (
              <>
                <span className="action-spark">+</span>
                Start autonomous review
              </>
            )}
          </button>
        </section>

        <section className="metric-grid">
          <article className="metric-card readiness-card">
            <div className="metric-card-top">
              <span>Permit readiness</span>
              <span className="trend-positive">+12%</span>
            </div>
            <div className="readiness-row">
              <div className="readiness-ring">
                <svg viewBox="0 0 72 72">
                  <circle className="ring-track" cx="36" cy="36" r="30" />
                  <circle
                    className="ring-value"
                    cx="36"
                    cy="36"
                    r="30"
                    pathLength="100"
                    strokeDasharray={`${project.readiness} 100`}
                  />
                </svg>
                <strong>{project.readiness}%</strong>
              </div>
              <div>
                <strong className="metric-primary">Nearly ready</strong>
                <span className="metric-secondary">
                  2 issues need attention
                </span>
              </div>
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-card-top">
              <span>Documents</span>
              <span className="metric-icon">DOC</span>
            </div>
            <strong className="big-number">
              {project.documentsAnalyzed}
              <span>/{project.documentsTotal}</span>
            </strong>
            <div className="metric-footer">
              <span className="success-dot" />
              Package analyzed
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-card-top">
              <span>Requirements</span>
              <span className="metric-icon">REQ</span>
            </div>
            <strong className="big-number">{project.permitsIdentified}</strong>
            <div className="metric-footer">
              Permit / review items identified
            </div>
          </article>

          <article className="metric-card">
            <div className="metric-card-top">
              <span>Issues detected</span>
              <span className="warning-icon">!</span>
            </div>
            <strong className="big-number warning-number">
              {project.issuesDetected}
            </strong>
            <div className="metric-footer">1 requires human judgment</div>
          </article>
        </section>

        <section className="dashboard-grid">
          <div className="main-column">
            <article className="panel">
              <div className="panel-header">
                <div>
                  <div className="section-label">PERMIT MATRIX</div>
                  <h3>Submission readiness</h3>
                </div>
                <button className="text-button">View all permits ?</button>
              </div>

              <div className="permit-table">
                <div className="permit-table-head">
                  <span>Permit / review</span>
                  <span>Authority</span>
                  <span>Readiness</span>
                  <span>Status</span>
                </div>

                {permits.map((permit) => (
                  <div className="permit-row" key={permit.id}>
                    <div className="permit-name">{permit.name}</div>
                    <div className="permit-authority">{permit.authority}</div>
                    <div className="permit-progress">
                      <div className="progress-track">
                        <div
                          className={`progress-value progress-${permit.status}`}
                          style={{ width: `${permit.readiness}%` }}
                        />
                      </div>
                      <span>{permit.readiness}%</span>
                    </div>
                    <StatusBadge status={permit.status} />
                  </div>
                ))}
              </div>
            </article>

            <article className="panel impact-panel">
              <div className="panel-header">
                <div>
                  <div className="section-label">MEASURABLE IMPACT</div>
                  <h3>Work PermitPilot is handling</h3>
                </div>
              </div>

              <div className="impact-grid">
                {impactMetrics.map((metric) => (
                  <div className="impact-item" key={metric.label}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                    <small>{metric.detail}</small>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <div className="side-column">
            <article
              className={`panel decision-panel ${
                decisionVisible ? "decision-panel-visible" : ""
              }`}
            >
              <div className="decision-kicker">
                <span>!</span>
                HUMAN DECISION REQUIRED
              </div>

              <h3>{decisions[0].title}</h3>
              <p className="decision-copy">
                PermitPilot found a material classification decision that should
                not be executed autonomously.
              </p>

              <div className="decision-confidence">
                <div>
                  <span>Agent confidence</span>
                  <strong>{decisions[0].confidence}%</strong>
                </div>
                <div className="confidence-track">
                  <div
                    style={{ width: `${decisions[0].confidence}%` }}
                    className="confidence-value"
                  />
                </div>
              </div>

              <div className="recommendation-box">
                <span>RECOMMENDATION</span>
                <p>{decisions[0].recommendation}</p>
              </div>

              <div className="impact-warning">
                <strong>Projected impact</strong>
                <span>{decisions[0].impact}</span>
              </div>

              <button className="evidence-button">
                Review {decisions[0].evidenceCount} evidence sources
              </button>

              <div className="decision-actions">
                <button className="secondary-button">Modify</button>
                <button
                  className="approve-button"
                  onClick={approveDecision}
                  disabled={!decisionVisible || reviewState === "approved"}
                >
                  {reviewState === "approved"
                    ? "? Recommendation approved"
                    : "Approve recommendation"}
                </button>
              </div>

              {reviewState === "idle" && (
                <div className="decision-overlay">
                  <span>Awaiting autonomous review</span>
                </div>
              )}

              {reviewState === "running" && (
                <div className="decision-overlay">
                  <span className="spinner dark-spinner" />
                  <span>Agent is evaluating risk...</span>
                </div>
              )}
            </article>

            <article className="panel activity-panel">
              <div className="panel-header compact-header">
                <div>
                  <div className="section-label">AGENT ACTIVITY</div>
                  <h3>Autonomous operations</h3>
                </div>
                <div className="live-badge">
                  <span />
                  LIVE
                </div>
              </div>

              <div className="activity-list">
                {activities.map((activity) => (
                  <div className="activity-item" key={activity.id}>
                    <div
                      className={`activity-node activity-${activity.status}`}
                    >
                      {activity.status === "complete" ? "?" : "!"}
                    </div>
                    <div className="activity-content">
                      <div className="activity-heading">
                        <strong>{activity.agent}</strong>
                        <span>{activity.timestamp}</span>
                      </div>
                      <p>{activity.action}</p>
                      <small>{activity.detail}</small>
                    </div>
                  </div>
                ))}
              </div>

              <button className="activity-footer">
                Open complete audit trail ?
              </button>
            </article>
          </div>
        </section>
      </main>
    </div>
  );
}
