"""Generate report-quality diagrams for the Candidate Lab project report.

All figures are deterministic vector-style drawings rendered to PNG so they can
be embedded in the Word report and exported to PDF without external services.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report-assets" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#142b40"
TEAL = "#126c68"
TEAL_LIGHT = "#dcefed"
LIGHT = "#eef3f5"
INK = "#17252e"
MUTED = "#5b6b75"
AMBER = "#8a5a12"
AMBER_LIGHT = "#fbf1dd"
WHITE = "#ffffff"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.linewidth": 0,
        "savefig.facecolor": WHITE,
    }
)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w * 10)
    ax.set_ylim(0, h * 10)
    ax.axis("off")
    return fig, ax


def box(
    ax,
    x,
    y,
    w,
    h,
    text,
    fc=LIGHT,
    ec=NAVY,
    fs=9,
    bold=False,
    rounded=0.18,
    lw=1.1,
    color=INK,
    z=2,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.25,rounding_size={rounded}",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
        zorder=z,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        color=color,
        fontweight="bold" if bold else "normal",
        zorder=z + 1,
        linespacing=1.45,
    )
    return patch


def arrow(
    ax,
    p1,
    p2,
    label="",
    rad=0.0,
    color=TEAL,
    lw=1.25,
    fs=7.6,
    both=False,
    dashed=False,
    lx=None,
    ly=None,
    z=1,
    ha="center",
):
    style = "<|-|>" if both else "-|>"
    patch = FancyArrowPatch(
        p1,
        p2,
        arrowstyle=style,
        mutation_scale=11,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        linestyle=(0, (4, 3)) if dashed else "solid",
        shrinkA=3,
        shrinkB=3,
        zorder=z,
    )
    ax.add_patch(patch)
    if label:
        mx = lx if lx is not None else (p1[0] + p2[0]) / 2
        my = ly if ly is not None else (p1[1] + p2[1]) / 2
        ax.text(
            mx,
            my,
            label,
            fontsize=fs,
            color=color,
            ha=ha,
            va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc=WHITE, ec="none", alpha=0.96),
            zorder=z + 2,
        )


def note(ax, x, y, text, fs=6.8, ha="center", style="italic", color=MUTED):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va="center", style=style)


def poly_arrow(ax, points, label="", lx=None, ly=None, fs=6.6, color=TEAL):
    """Draw an orthogonal connector with an arrow head on the final segment."""
    for p, q in zip(points[:-1], points[1:]):
        ax.plot([p[0], q[0]], [p[1], q[1]], color=color, linewidth=1.25,
                zorder=1, solid_capstyle="round")
    p, q = points[-2], points[-1]
    ax.add_patch(
        FancyArrowPatch(
            p,
            q,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.25,
            color=color,
            shrinkA=0,
            shrinkB=0,
            zorder=2,
        )
    )
    if label:
        ax.text(lx, ly, label, fontsize=fs, color=color, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc=WHITE, ec="none", alpha=0.96), zorder=3)


# ---------------------------------------------------------------- architecture
def architecture():
    fig, ax = canvas(11.6, 7.2)
    bands = [
        (52, 19, "Presentation layer", "#f5f9fa"),
        (38, 13, "Application and API layer", "#edf5f4"),
        (20, 17, "Domain services", "#f8fafb"),
        (3, 16, "Data and model layer", "#f1f5f7"),
    ]
    for y, h, label, color in bands:
        ax.add_patch(
            FancyBboxPatch(
                (1.5, y + 0.6),
                112,
                h - 1.2,
                boxstyle="round,pad=0.25,rounding_size=0.5",
                linewidth=0.8,
                edgecolor="#c8d6dc",
                facecolor=color,
                zorder=0,
            )
        )
        ax.text(2.6, y + h - 1.0, label, fontsize=7.6, color=MUTED, va="top", fontweight="bold")

    box(ax, 4, 61, 30, 7, "Candidate browser\nReact + TypeScript", fs=8.2)
    box(ax, 41, 61, 30, 7, "Recruiter browser\nReact + TypeScript", fs=8.2)
    box(ax, 78, 61, 30, 7, "Auditor browser\nReact + TypeScript", fs=8.2)

    box(
        ax,
        4,
        54,
        104,
        5.6,
        "Role-based single-page interface · register · profiles · jobs · applications · evidence · review · audit",
        fs=8.2,
        fc=TEAL_LIGHT,
    )
    arrow(ax, (19, 61), (19, 59.6))
    arrow(ax, (56, 61), (56, 59.6))
    arrow(ax, (93, 61), (93, 59.6))

    box(
        ax,
        4,
        40,
        104,
        6,
        "FastAPI application boundary\nSession and role dependencies · Pydantic validation · origin and size limits · static assets",
        fs=8.2,
        fc=TEAL_LIGHT,
    )
    arrow(ax, (56, 54), (56, 46), "HTTPS · JSON and multipart", fs=6.9, lx=71.5, ly=50)

    services = [
        (2.5, 23, 19.5, 11, "Authentication\nPBKDF2 · sessions\ninvitations"),
        (24.8, 23, 19.5, 11, "Profile service\nparse · extract\nversion history"),
        (47.1, 23, 19.5, 11, "Job service\nrubric validation\npublication state"),
        (69.4, 23, 19.5, 11, "Applications\nsnapshot · revision\ndecision workflow"),
        (91.7, 23, 19.8, 11, "Matching service\nTF-IDF or semantic\nevidence and score"),
    ]
    for x, y, w, h, t in services:
        box(ax, x, y, w, h, t, fs=7.3, lw=0.9)
    arrow(ax, (56, 40), (56, 34), "service calls", fs=6.8, lx=63, ly=37)

    box(ax, 8, 6, 27, 10, "SQLite (default)\nor PostgreSQL", fs=7.9, fc="#f7fafb")
    box(ax, 41, 6, 30, 10, "SQLAlchemy ORM\nrecord persistence", fs=7.9, fc="#f7fafb")
    box(ax, 77, 6, 25, 10, "Local semantic model\noptional · offline", fs=7.9, fc="#f7fafb")
    arrow(ax, (56, 23), (56, 16), "ORM queries and commits", fs=6.8, lx=71, ly=19.4)
    note(
        ax,
        109,
        1.1,
        "Matching reads submitted snapshots only; audit attributes never enter the ranking path.",
        fs=6.4,
        ha="right",
    )

    fig.savefig(OUT / "architecture.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ------------------------------------------------------------------------ DFD 0
def dfd0():
    fig, ax = canvas(12.0, 6.4)
    cx, cy, r = 57, 32, 12.5
    ax.add_patch(Circle((cx, cy), r, facecolor=TEAL_LIGHT, edgecolor=NAVY, linewidth=1.4, zorder=2))
    ax.text(cx, cy + 4.4, "0", fontsize=15, color=NAVY, ha="center", va="center", fontweight="bold", zorder=3)
    ax.text(cx, cy - 3.2, "Candidate Lab\nmatching and review", fontsize=8.4, color=INK, ha="center", va="center", zorder=3)

    box(ax, 3, 52, 23, 8, "Candidate", fs=9, fc=WHITE, bold=True)
    box(ax, 3, 6, 23, 8, "Recruiter", fs=9, fc=WHITE, bold=True)
    box(ax, 92, 28, 24, 8, "Auditor", fs=9, fc=WHITE, bold=True)

    # Candidate supplies evidence and applications; receives application status.
    arrow(ax, (26, 57.5), (51.7, 43.3), "profile evidence and\napplications", lx=35, ly=54.6, fs=7.1)
    arrow(ax, (46.8, 39.2), (26, 53.5), "application\nstatus", lx=34.5, ly=45.4, fs=7.1)

    # Recruiter publishes rubrics and requests review; receives ranked evidence.
    arrow(ax, (26, 13.5), (44.9, 35.2), "job rubrics, publish and\nreview requests", lx=35.5, ly=27.4, fs=7.1)
    arrow(ax, (46.8, 24.8), (26, 8.5), "ranked evidence and\nreview history", lx=38, ly=11.6, fs=7.1)

    # Auditor receives aggregate reporting and sets the reporting cutoff.
    arrow(ax, (69.5, 34.4), (92, 33.8), "aggregate cohort report\nand audit events", lx=80.7, ly=37.0, fs=7.2)
    arrow(ax, (92, 30.2), (69.5, 29.6), "cutoff and\nreport request", lx=80.7, ly=27.0, fs=7.2)

    note(ax, 60, 2.3, "Level 0 context diagram: external interactions only", fs=7.4)
    fig.savefig(OUT / "dfd_level0.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ------------------------------------------------------------------------ DFD 1
def dfd1():
    fig, ax = canvas(16.4, 9.6)
    # external entities
    box(ax, 2, 75, 20, 9, "Candidate", fs=9, fc=WHITE, bold=True)
    box(ax, 2, 45, 20, 20, "Recruiter", fs=9, fc=WHITE, bold=True)
    box(ax, 2, 4, 20, 8, "Auditor", fs=9, fc=WHITE, bold=True)

    # processes
    procs = [
        (50, 74, 27, 9, "1. Manage account\nand profile evidence"),
        (50, 60, 27, 9, "2. Manage jobs and\npublication state"),
        (50, 46, 27, 9, "3. Submit application\n(snapshot + revision)"),
        (50, 32, 27, 9, "4. Rank active\napplications"),
        (50, 18, 27, 9, "5. Review and record\ndecision"),
        (50, 4, 27, 9, "6. Audit and model\nevaluation"),
    ]
    for x, y, w, h, t in procs:
        box(ax, x, y, w, h, t, fs=8.0, fc=TEAL_LIGHT)

    # data stores
    stores = [
        (118, 78, 42, 6.5, "D1  Users, sessions and invitations"),
        (118, 70.5, 42, 6.5, "D2  Profiles and profile versions"),
        (118, 62.5, 42, 6.5, "D3  Jobs and publications"),
        (118, 48, 42, 6.5, "D4  Applications and versions"),
        (118, 34.5, 42, 6.5, "D5  Runs, reviews and decisions"),
        (118, 5.5, 42, 6.5, "D6  Audit log, attributes and evaluations"),
    ]
    for x, y, w, h, t in stores:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.18,rounding_size=0.08",
                facecolor=WHITE,
                edgecolor=NAVY,
                linewidth=1.0,
                zorder=2,
            )
        )
        ax.plot([x + 3.2, x + 3.2], [y, y + h], color=NAVY, linewidth=0.9, zorder=3)
        ax.text(x + 4.3, y + h / 2, t, fontsize=6.7, va="center", color=INK, zorder=4)

    # candidate flows
    arrow(ax, (22, 80.5), (50, 79.5), "credentials and profile evidence", lx=36, ly=82.4, fs=6.6)
    arrow(ax, (50, 77.5), (22, 78.5), "profile status", lx=36, ly=75.6, fs=6.6)
    poly_arrow(ax, [(24, 75), (24, 57.2), (55, 57.2), (55, 55.2)],
               "application and profile correction", lx=36, ly=58.6, fs=6.6)

    # recruiter flows (out and back, ordered so lines never cross)
    arrow(ax, (22, 62), (50, 64.5), "job rubric and\npublish request", lx=36, ly=66.3, fs=6.6)
    arrow(ax, (22, 57), (50, 36.5), "matching request", lx=27.5, ly=53.2, fs=6.6)
    arrow(ax, (50, 34.5), (22, 54), "ranked evidence", lx=30.5, ly=42.6, fs=6.6)
    arrow(ax, (22, 51), (50, 22.5), "review and\ndecision request", lx=37, ly=34.0, fs=6.6)
    arrow(ax, (50, 20.5), (22, 47.5), "review history", lx=37, ly=24.2, fs=6.6)

    # auditor flows
    arrow(ax, (22, 9), (50, 9), "cutoff and report request", lx=36, ly=11.0, fs=6.6)
    arrow(ax, (50, 6.2), (22, 6.2), "aggregate audit report", lx=36, ly=7.7, fs=6.6)

    # process-to-store flows
    arrow(ax, (77, 79.5), (118, 79.5), "", both=True)
    ax.text(97, 81.3, "account, session and invitation records", fontsize=6.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none"))
    arrow(ax, (77, 75.5), (118, 72.8), "profile records and versions", lx=97.5, ly=75.5, fs=6.5)
    arrow(ax, (77, 64.8), (118, 64.8), "", both=True)
    ax.text(97, 66.6, "job rubric versions and publication", fontsize=6.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none"))
    arrow(ax, (77, 51), (118, 51), "", both=True)
    ax.text(97, 52.8, "application snapshot and revision", fontsize=6.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none"))
    arrow(ax, (77, 37.5), (118, 37.5), "", both=True)
    ax.text(97, 39.3, "scores, requirement evidence and run snapshot", fontsize=6.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none"))
    arrow(ax, (77, 21.5), (118, 37), "decision and\nreview history", lx=97, ly=25.8, fs=6.5)
    arrow(ax, (77, 8.8), (118, 8.8), "", both=True)
    ax.text(97, 10.6, "aggregate audit, events and evaluations", fontsize=6.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none"))

    # pipeline flows
    arrow(ax, (63.5, 60), (63.5, 55), "job rubric", lx=69.5, ly=57.5, fs=6.5)
    arrow(ax, (63.5, 46), (63.5, 41), "application snapshots", lx=71, ly=43.5, fs=6.5)
    arrow(ax, (63.5, 32), (63.5, 27), "ranked evidence", lx=69.5, ly=29.5, fs=6.5)
    arrow(ax, (63.5, 18), (63.5, 13), "review history", lx=69.5, ly=15.5, fs=6.5)

    note(ax, 82, 1.4, "Level 1 data flow: numbered processes, shared data stores D1-D6 and external entities", fs=7.2)
    fig.savefig(OUT / "dfd_level1.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ------------------------------------------------------------------ class diagram
def cls(ax, x, y, w, h, name, attrs, color=LIGHT):
    box(ax, x, y, w, h, "", fc=WHITE, lw=1.0)
    ax.add_patch(
        FancyBboxPatch(
            (x, y + h - 2.4),
            w,
            2.4,
            boxstyle="round,pad=0.16,rounding_size=0.1",
            facecolor=color,
            edgecolor=NAVY,
            linewidth=1.0,
            zorder=3,
        )
    )
    ax.text(x + w / 2, y + h - 1.2, name, fontsize=7.9, fontweight="bold", color=NAVY,
            ha="center", va="center", zorder=4)
    ax.text(x + 0.5, y + h - 3.2, attrs, fontsize=6.0, color=INK, ha="left", va="top",
            linespacing=1.25, zorder=4)


def class_diagram():
    fig, ax = canvas(15.6, 9.4)
    w, h = 21, 14.5
    xs = [2, 32, 62, 92]
    ys = [70, 50, 30, 8]
    teal = "#e4f0ef"

    def c(col, row, name, attrs, color=LIGHT):
        cls(ax, xs[col], ys[row], w, h, name, attrs, color)

    c(0, 0, "User", "id : str «PK»\nemail : str «unique»\nrole : candidate |\n       recruiter | auditor\npassword : text", teal)
    c(1, 0, "Candidate", "id : str «PK»\nowner_id : str «FK»\nlabel : str\ntext : text\nskills, warnings : JSON[]\nversion, synthetic : int/bool", teal)
    c(2, 0, "ProfileVersion", "id : str «PK»\ncandidate_id : str «FK»\nversion : int\ntext : text\ncreated : timestamp")

    c(0, 1, "Job", "id : str «PK»\ntitle : str\ndescription : text\nrequired, preferred : JSON[]\nversion : int\ncreated : timestamp", teal)
    c(1, 1, "Application", "id : str «PK»\njob_id : str «FK»\nowner_id : str «FK»\ncandidate_id : str «FK»\nsnapshot : JSON\nstatus : enum\nrevision : int\ncreated, updated : timestamp", teal)
    c(2, 1, "ApplicationVersion", "id : str «PK»\napplication_id : str «FK»\nrevision : int\nsnapshot : JSON\nstatus : str\ncreated : timestamp")

    c(0, 2, "Run", "id : str «PK»\njob_id : str «FK»\njob_snapshot : JSON\nmethod : str\nresults : JSON[]\ncreated : timestamp", teal)
    c(1, 2, "Review", "id : str «PK»\nrun_id : str «FK»\ncandidate_id : str «FK»\nreviewer_id : str «FK»\nstatus : enum\nreason : text\ncreated : timestamp", teal)
    c(2, 2, "RecruitmentDecision", "id : str «PK»\napplication_id : str «FK»\nrecruiter_id : str «FK»\nstatus : enum\nfeedback : text\nrevision : int\ncreated : timestamp", teal)
    c(3, 2, "DecisionEvidence", "decision_id : str «PK»\nrun_id : str «FK»\nevidence : JSON")

    # audit / evaluation records in a separate dashed context
    ax.add_patch(
        FancyBboxPatch((2, 6), 111, 18.5, boxstyle="round,pad=0.25,rounding_size=0.5",
                       fill=False, edgecolor="#c6d3d8", linewidth=0.9, linestyle=(0, (4, 3)))
    )
    ax.text(3.2, 26.0, "Separate audit and evaluation context — never a ranking input",
            fontsize=6.8, color=MUTED, va="center", style="italic")
    c(0, 3, "AuditAttribute", "candidate_id : str «PK»\ngroup : str\nsynthetic : bool")
    c(1, 3, "AuditLog", "id : str «PK»\nactor_id : str «FK»\naction : str\nobject_id : str\ncreated : timestamp")
    c(2, 3, "Evaluation", "id : str «PK»\ndataset : JSON\nreport : JSON\ncreated : timestamp")

    def card(x1, x2, y, left, right):
        arrow(ax, (x1, y), (x2, y), "", color=NAVY, lw=0.9, z=1)
        ax.text(x1 + 1.1, y + 0.85, left, fontsize=6.4, color=NAVY, ha="left", va="center")
        ax.text(x2 - 1.1, y + 0.85, right, fontsize=6.4, color=NAVY, ha="right", va="center")

    def vcard(x, y1, y2, label):
        arrow(ax, (x, y1), (x, y2), "", color=NAVY, lw=0.9, z=1)
        ax.text(x + 1.4, (y1 + y2) / 2, label, fontsize=6.2, color=NAVY, ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc=WHITE, ec="none"))

    # horizontal associations at mid-height, cardinalities in the 9-unit gaps
    card(2 + w, 32, 77, "1", "0..*")
    card(32 + w, 62, 77, "1", "0..*")
    card(2 + w, 32, 57, "1", "0..*")
    card(32 + w, 62, 57, "1", "0..*")
    card(2 + w, 32, 37, "1", "0..*")
    card(62 + w, 92, 37, "1", "1")

    # vertical and diagonal associations
    vcard(42.5, 70, 64.5, "1 submits  0..*")
    vcard(12.5, 50, 44.5, "1 runs  0..*")
    arrow(ax, (53, 52), (72.5, 44.5), "", color=NAVY, lw=0.9, z=1)
    ax.text(60, 47.0, "1 produces  0..*", fontsize=6.2, color=NAVY, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc=WHITE, ec="none"))

    ax.text(2, 1.6, "PK = primary identifier; FK = application-level reference.",
            fontsize=6.4, color=MUTED, va="center", style="italic")
    ax.text(113, 1.6, "Publication is a 1:1 job state record keyed by job_id; Review also references candidate_id and reviewer_id.",
            fontsize=6.4, color=MUTED, va="center", ha="right", style="italic")
    fig.savefig(OUT / "class_diagram.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# --------------------------------------------------------------- sequence diagram
def sequence():
    fig, ax = canvas(14.6, 9.3)
    lanes = [(14, "Candidate"), (34, "React UI"), (58, "FastAPI\napplication"),
             (82, "Matching\nservice"), (106, "Database"), (132, "Recruiter")]
    top = 84
    bottom = 7
    for x, label in lanes:
        box(ax, x - 8.2, top, 16.4, 7, label, fs=8.4, fc="#e4f0ef", bold=True)
        ax.plot([x, x], [bottom, top - 0.4], color="#b9c8ce", linewidth=1.0,
                linestyle=(0, (5, 4)), zorder=0)

    msgs = [
        (14, 34, 77.5, "select saved profile and apply", False),
        (34, 58, 73.0, "POST /api/jobs/{id}/applications", False),
        (58, 106, 68.5, "load profile, job and publication", False),
        (106, 58, 64.0, "profile snapshot and active status", True),
        (58, 106, 59.5, "insert Application and ApplicationVersion", False),
        (58, 34, 55.0, "201 application · revision 1", True),
        (34, 14, 50.5, "confirmation and application status", True),
        (132, 34, 46.0, "open applicants and run matching", False),
        (34, 58, 41.5, "POST /api/jobs/{id}/runs", False),
        (58, 106, 37.0, "load active application snapshots", False),
        (106, 58, 32.5, "submitted profile versions", True),
        (58, 82, 28.0, "rank(job, profiles, method)", False),
        (82, 58, 23.5, "scores, requirement evidence, contributions", True),
        (58, 106, 19.0, "insert immutable run snapshot", False),
        (58, 34, 14.5, "201 saved run", True),
        (34, 132, 10.0, "ranking and evidence ledger", True),
    ]
    for x1, x2, y, text, dashed in msgs:
        arrow(ax, (x1, y), (x2, y), "", color=MUTED if dashed else TEAL,
              lw=1.05, dashed=dashed, z=1)
        ax.text((x1 + x2) / 2, y + 1.15, text, fontsize=7.1, color=INK, ha="center",
                va="bottom", bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none", alpha=0.96))

    note(ax, 73, 2.6, "Solid arrows are requests; dashed arrows are responses. A saved run is immutable.", fs=7.0)
    fig.savefig(OUT / "sequence_diagram.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ------------------------------------------------------------------- state chart
def state_chart():
    fig, ax = canvas(12.2, 6.6)
    ax.add_patch(Circle((8, 48), 1.4, color=NAVY, zorder=3))
    note(ax, 8, 50.8, "start", fs=7.2, style="normal")

    states = [
        (22, 40, 24, 14, "Submitted\n(active)", "#e4f0ef"),
        (62, 40, 24, 14, "Under review\n(under_review)", "#f7f0dc"),
        (96, 52, 22, 11, "Accepted\n(accepted)", "#dff0e4"),
        (96, 31, 22, 11, "Rejected\n(rejected)", "#f8e7e9"),
    ]
    for x, y, w, h, t, fc in states:
        box(ax, x, y, w, h, t, fs=8.7, fc=fc, bold=False)

    arrow(ax, (9.4, 48), (22, 47), "application created", lx=15.5, ly=55.7, fs=7.0)
    arrow(ax, (46, 47), (62, 47), "open review", lx=54, ly=49.2, fs=7.0)
    arrow(ax, (86, 50.5), (96, 55.5), "accept", lx=90, ly=54.8, fs=7.0)
    arrow(ax, (86, 43.5), (96, 38.5), "reject", lx=90, ly=40.2, fs=7.0)

    # revision self-loops
    for x, y, w, h, label in [
        (22, 40, 24, 14, "revise"),
        (62, 40, 24, 14, "re-decide"),
    ]:
        ax.add_patch(
            FancyArrowPatch(
                (x + w * 0.32, y + h),
                (x + w * 0.68, y + h),
                arrowstyle="-|>",
                mutation_scale=10,
                color=TEAL,
                connectionstyle="arc3,rad=-0.8",
                linewidth=1.0,
                zorder=1,
            )
        )
        note(ax, x + w / 2, y + h + 4.7, label, fs=6.8, style="normal", color=TEAL)

    # withdrawn is a legacy state only
    box(ax, 22, 20, 24, 12, "Withdrawn\n(legacy record)", fs=8.1, fc="#f1f3f4", ec=MUTED, color=MUTED)
    arrow(ax, (34, 40), (34, 32), "", color=MUTED, dashed=True, z=1)
    ax.text(36.5, 36.2, "historical data only", fontsize=6.8, color=MUTED, ha="left", va="center")

    note(ax, 22, 15.5, "Withdrawal returns HTTP 410; the state is retained\nonly for older records.", fs=6.8, ha="left")
    note(ax, 118, 23.5, "Decision updates append a new revision and\nimmutable evidence. Scores are never rewritten.",
         fs=6.9, ha="right")
    ax.set_xlim(2, 119)
    ax.set_ylim(12, 65)
    fig.savefig(OUT / "state_chart.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ---------------------------------------------------------------- activity chart
def diamond(ax, cx, cy, w, h, text, fc=AMBER_LIGHT, ec=AMBER, fs=7.6):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(plt.Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.1, zorder=2))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=INK, zorder=3, linespacing=1.35)


def activity():
    fig, ax = canvas(10.8, 13.2)
    cx = 42
    ax.add_patch(Circle((cx, 127.5), 1.5, color=NAVY, zorder=3))
    note(ax, cx, 130.0, "start", fs=7.0, style="normal")

    box(ax, cx - 16, 118, 32, 7, "Sign in and resolve role", fs=8.0)
    arrow(ax, (cx, 126.0), (cx, 125.2))
    box(ax, cx - 17, 108, 34, 7, "Add or correct profile evidence", fs=8.0)
    arrow(ax, (cx, 118), (cx, 115))
    box(ax, cx - 18, 98, 36, 7, "Preview extraction and evidence passages", fs=8.0)
    arrow(ax, (cx, 108), (cx, 105))

    diamond(ax, cx, 90, 30, 9, "Evidence accepted?")
    arrow(ax, (cx, 98), (cx, 94.5))
    arrow(ax, (cx - 15, 90), (23, 88.5), "no", lx=25, ly=92.2, fs=7.0)
    box(ax, 2, 84, 21, 8.5, "Correct text or add\nsupported evidence", fs=7.2)
    arrow(ax, (12.5, 92.5), (26, 101.5), "re-preview", rad=-0.18, fs=6.9, lx=14.0, ly=99.6)

    arrow(ax, (cx, 85.5), (cx, 79.5), "yes", lx=43.5, ly=82.6, fs=7.0)
    box(ax, cx - 20, 71.5, 40, 8, "Save profile version", fs=7.9)
    arrow(ax, (cx, 71.5), (cx, 67.5))
    box(ax, cx - 20, 59.5, 40, 8, "Recruiter publishes the job", fs=7.9)
    arrow(ax, (cx, 59.5), (cx, 55.5))
    box(ax, cx - 20, 47.5, 40, 8, "Candidate applies with a profile snapshot", fs=7.7)
    arrow(ax, (cx, 47.5), (cx, 43))
    box(ax, cx - 22, 34, 44, 9, "Rank active submitted snapshots\n(TF-IDF or local semantic model)", fs=7.4, fc=TEAL_LIGHT)
    arrow(ax, (cx, 34), (cx, 29))
    box(ax, cx - 24, 21, 48, 8, "Save immutable run and inspect\nrequirement evidence", fs=7.4)
    arrow(ax, (cx, 21), (cx, 17))

    box(ax, cx - 24, 9, 48, 8, "Record decision revision and\nappend immutable evidence", fs=7.4)
    arrow(ax, (cx, 9), (cx, 5.3))
    ax.add_patch(Circle((cx, 4.0), 1.5, facecolor=WHITE, edgecolor=NAVY, linewidth=1.2, zorder=3))
    ax.add_patch(Circle((cx, 4.0), 0.62, color=NAVY, zorder=4))
    note(ax, cx + 3, 3.8, "end", fs=7.0, style="normal")

    # auditor receives the immutable audit trail
    arrow(ax, (cx + 24, 25), (74, 20), "audit trail", lx=68.5, ly=24.0, fs=6.9)
    box(ax, 74, 9, 30, 11, "Auditor reviews aggregate\ncohort report and\naudit events", fs=7.2, fc="#f5f8f9")

    note(ax, 54, 0.4, "Primary flow; the evidence-correction loop is shown on the left.", fs=6.8)
    fig.savefig(OUT / "activity_diagram.png", dpi=230, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    dfd0()
    dfd1()
    class_diagram()
    sequence()
    state_chart()
    activity()
    for path in sorted(OUT.glob("*.png")):
        print(path.name, path.stat().st_size)
