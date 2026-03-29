"""Render the final PawPal+ UML class diagram to uml_final.png using matplotlib."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ── Layout constants ─────────────────────────────────────────────────────────
FIG_W, FIG_H = 18, 15
BG = "#1a1a1a"
BOX_BG = "#2b2b2b"
HEADER_BG = "#111111"
TEXT_COLOR = "#e8e8e8"
ACCENT = "#6eb5ff"         # attribute colour
METHOD_COLOR = "#b5e8b5"   # method colour
ARROW_COLOR = "#aaaaaa"
COMP_COLOR = "#ffcc66"     # composition diamond colour
DEP_COLOR = "#88ccff"      # dependency arrow colour

FONT_TITLE = dict(fontsize=11, fontweight="bold", color=TEXT_COLOR, fontfamily="monospace")
FONT_ATTR   = dict(fontsize=8.5, color=ACCENT, fontfamily="monospace")
FONT_METHOD = dict(fontsize=8.5, color=METHOD_COLOR, fontfamily="monospace")
FONT_LABEL  = dict(fontsize=7, color=ARROW_COLOR, fontfamily="monospace",
                   ha="center", va="center",
                   bbox=dict(boxstyle="round,pad=0.15", fc=BG, ec="none"))

# ── Class box data ────────────────────────────────────────────────────────────
# Each entry: (name, x, y, width, height, attributes, methods)
# Coordinates are in figure-fraction units (0-1)
classes = [
    (
        "Task",
        0.52, 0.03, 0.44, 0.46,
        [
            "task_id : str",
            "pet_name : str",
            "task_type : str",
            "duration_minutes : int",
            "priority : int",
            "preferred_time : time  [optional]",
            "status : str  = 'pending'",
            "frequency : str  = 'once'   ★",
            "due_date : date  [optional]  ★",
        ],
        [
            "mark_done()",
            "next_occurrence(counter) : Task  ★",
            "reschedule(new_time)",
            "update_details(**kwargs)",
        ],
    ),
    (
        "Pet",
        0.04, 0.28, 0.44, 0.36,
        [
            "name : str",
            "species : str",
            "breed : str  [optional]",
            "age : int  [optional]",
            "health_notes : str  [optional]",
            "care_requirements : Dict[str,str]",
            "tasks : List[Task]  ★",
        ],
        [
            "update_health_notes(notes)",
            "describe() : str",
            "needs_task(task_type) : bool",
            "add_task(task)  ★",
        ],
    ),
    (
        "Owner",
        0.04, 0.68, 0.44, 0.30,
        [
            "name : str",
            "contact_info : str",
            "preferences : Dict[str,str]",
            "available_time_slots : List[str]",
            "pets : List[Pet]  ★",
        ],
        [
            "update_preferences(new_prefs)",
            "set_availability(slots)",
            "add_pet(pet)  ★",
            "get_summary() : Dict",
            "get_all_tasks() : List[Task]  ★",
        ],
    ),
    (
        "Scheduler",
        0.52, 0.53, 0.44, 0.45,
        [
            "date : datetime",
            "assigned_tasks : List[Task]",
            "constraints : Dict[str,str]",
            "plan_description : str  [optional]",
        ],
        [
            "generate_plan(owner) : List[Task]",
            "sort_by_time() : List[Task]  ★",
            "filter_tasks(pet_name, status)  ★",
            "mark_task_complete(task_id, owner)  ★",
            "score_task_order() : float",
            "conflict_check() : bool",
            "get_conflict_warnings() : List[str]  ★",
            "get_todays_tasks() : List[Task]",
        ],
    ),
]

# ── Draw a class box ──────────────────────────────────────────────────────────
def draw_class(ax, name, x, y, w, h, attrs, methods):
    """Draw a UML class box in figure-fraction space."""
    # Outer border
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.005",
        linewidth=1.2, edgecolor=ACCENT, facecolor=BOX_BG,
        transform=ax.transAxes, zorder=2,
    )
    ax.add_patch(rect)

    # Estimate row heights
    total_rows = 1 + len(attrs) + 1 + len(methods)   # header + attrs + divider + methods
    row_h = h / (total_rows + 0.5)

    # Header band
    header_h = row_h * 1.2
    header = mpatches.FancyBboxPatch(
        (x, y + h - header_h), w, header_h,
        boxstyle="round,pad=0.005",
        linewidth=0, facecolor=HEADER_BG,
        transform=ax.transAxes, zorder=3,
    )
    ax.add_patch(header)

    # Class name
    ax.text(x + w / 2, y + h - header_h / 2, f"«class»  {name}",
            transform=ax.transAxes, ha="center", va="center", zorder=4, **FONT_TITLE)

    # Divider after attributes
    div_y = y + h - header_h - (len(attrs) + 0.3) * row_h
    ax.plot([x + 0.005, x + w - 0.005], [div_y, div_y],
            color=ACCENT, linewidth=0.6, alpha=0.5, transform=ax.transAxes, zorder=3)

    # Attribute rows
    for i, attr in enumerate(attrs):
        row_y = y + h - header_h - (i + 0.85) * row_h
        ax.text(x + 0.015, row_y, f"  {attr}",
                transform=ax.transAxes, ha="left", va="center", zorder=4, **FONT_ATTR)

    # Method rows
    for j, method in enumerate(methods):
        row_y = y + h - header_h - (len(attrs) + 0.9 + j + 0.4) * row_h
        ax.text(x + 0.015, row_y, f"  +{method}",
                transform=ax.transAxes, ha="left", va="center", zorder=4, **FONT_METHOD)


# ── Arrow helpers ─────────────────────────────────────────────────────────────
def midpoint(cls, side="right"):
    """Return the (x, y) figure-fraction midpoint of a class box side."""
    x, y, w, h = cls[1], cls[2], cls[3], cls[4]
    if side == "right":  return (x + w, y + h / 2)
    if side == "left":   return (x, y + h / 2)
    if side == "top":    return (x + w / 2, y + h)
    if side == "bottom": return (x + w / 2, y)


def arrow(ax, x0, y0, x1, y1, style="-|>", color=ARROW_COLOR, lw=1.2,
          label=None, label_x=None, label_y=None, dashed=False):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, linestyle=ls),
                zorder=5)
    if label:
        lx = label_x if label_x else (x0 + x1) / 2
        ly = label_y if label_y else (y0 + y1) / 2
        ax.text(lx, ly, label, transform=ax.transAxes, zorder=6, **FONT_LABEL)


# ── Build figure ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Draw all class boxes
for cls in classes:
    draw_class(ax, *cls)

# Resolve class lookup by name for midpoint calculations
cls_map = {c[0]: c for c in classes}

# ── Relationships ─────────────────────────────────────────────────────────────

# Owner ◆──────── Pet   (composition: Owner owns 0..* Pets)
ox, oy = midpoint(cls_map["Owner"], "bottom")
px, py = midpoint(cls_map["Pet"], "top")
arrow(ax, ox, oy, px, py,
      style="-|>", color=COMP_COLOR, lw=1.4,
      label="owns  1 ◆ → 0..*", label_x=0.175, label_y=(oy + py) / 2)

# Pet ◆──────── Task   (composition: Pet has 0..* Tasks)
px2, py2 = midpoint(cls_map["Pet"], "right")
tx, ty = midpoint(cls_map["Task"], "left")
arrow(ax, px2, py2, tx, ty,
      style="-|>", color=COMP_COLOR, lw=1.4,
      label="has  1 ◆ → 0..*", label_x=0.5, label_y=(py2 + ty) / 2 + 0.015)

# Scheduler ..-> Owner   (dependency: generate_plan(owner))
sx, sy = midpoint(cls_map["Scheduler"], "left")
ox2, oy2 = midpoint(cls_map["Owner"], "right")
arrow(ax, sx, sy, ox2, oy2,
      style="-|>", color=DEP_COLOR, lw=1.1, dashed=True,
      label="uses  (generate_plan)", label_x=0.365, label_y=(sy + oy2) / 2 - 0.02)

# Scheduler ..-> Task   (dependency: assigns tasks)
sx2, sy2 = midpoint(cls_map["Scheduler"], "bottom")
tx2, ty2 = midpoint(cls_map["Task"], "top")
arrow(ax, sx2, sy2, tx2, ty2,
      style="-|>", color=DEP_COLOR, lw=1.1, dashed=True,
      label="assigns", label_x=0.765, label_y=(sy2 + ty2) / 2)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_x, legend_y = 0.04, 0.02
ax.text(legend_x, legend_y + 0.06, "Legend", transform=ax.transAxes,
        fontsize=8, fontweight="bold", color=TEXT_COLOR, fontfamily="monospace")
ax.plot([legend_x, legend_x + 0.04], [legend_y + 0.04, legend_y + 0.04],
        color=COMP_COLOR, lw=1.4, transform=ax.transAxes)
ax.text(legend_x + 0.045, legend_y + 0.04, "Composition",
        transform=ax.transAxes, fontsize=7, color=TEXT_COLOR, va="center", fontfamily="monospace")
ax.plot([legend_x, legend_x + 0.04], [legend_y + 0.02, legend_y + 0.02],
        color=DEP_COLOR, lw=1.1, linestyle=(0, (4, 3)), transform=ax.transAxes)
ax.text(legend_x + 0.045, legend_y + 0.02, "Dependency",
        transform=ax.transAxes, fontsize=7, color=TEXT_COLOR, va="center", fontfamily="monospace")
ax.text(legend_x, legend_y, "  ★ = added since initial UML",
        transform=ax.transAxes, fontsize=7, color="#ffaa55", fontfamily="monospace")

# Title
ax.text(0.5, 0.98, "PawPal+ — Final UML Class Diagram",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=13, fontweight="bold", color=TEXT_COLOR, fontfamily="monospace")

plt.tight_layout(pad=0.3)
plt.savefig("uml_final.png", dpi=150, bbox_inches="tight", facecolor=BG)
print("Saved uml_final.png")
