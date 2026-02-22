import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Ellipse, Polygon

# Create figure and axis (landscape-ish proportions)
fig, ax = plt.subplots(figsize=(14, 11))
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.axis('off')

# Helper: Draw rectangular node with rounded look via FancyBboxPatch
def draw_rect_node(x, y, text_lines, width=4.2, height=1.5, facecolor='lightblue'):
    rect = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.08",
        facecolor=facecolor,
        edgecolor="black",
        lw=1.3,
    )
    ax.add_patch(rect)
    for i, line in enumerate(text_lines):
        ax.text(x, y + (len(text_lines)-1-i)*0.4 - 0.15*(len(text_lines)-1),
                line, ha='center', va='center', fontsize=9.5, wrap=True)

# Helper: Diamond (decision)
def draw_diamond(x, y, text_lines, size=3.2):
    points = [
        (x, y + size/2),           # top
        (x + size/2, y),           # right
        (x, y - size/2),           # bottom
        (x - size/2, y)            # left
    ]
    diamond = Polygon(points, closed=True, facecolor='lightcoral',
                      edgecolor='black', lw=1.3)
    ax.add_patch(diamond)
    for i, line in enumerate(text_lines):
        ax.text(x, y + (len(text_lines)-1-i)*0.35 - 0.1*(len(text_lines)-1),
                line, ha='center', va='center', fontsize=9.5)

# Helper: Ellipse (start/stop/output)
def draw_ellipse_node(x, y, text_lines, width=4, height=1.3, facecolor='lightgreen'):
    ellipse = Ellipse((x, y), width, height,
                      facecolor=facecolor, edgecolor='black', lw=1.3)
    ax.add_patch(ellipse)
    for i, line in enumerate(text_lines):
        ax.text(x, y + (len(text_lines)-1-i)*0.35 - 0.1*(len(text_lines)-1),
                line, ha='center', va='center', fontsize=9.5)

# Arrow helper with optional label
def draw_arrow(start, end, label=None, label_pos='mid', offset=(0, 0.25)):
    arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=22,
                            linewidth=1.6, color='black')
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + offset[0]
        my = (start[1] + end[1]) / 2 + offset[1]
        ax.text(mx, my, label, fontsize=10, ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', pad=2, alpha=0.95))

# ────────────────────────────────────────────────
# Nodes (top to bottom)

draw_ellipse_node(7, 11, ['Start: Input Tweet'], facecolor='lightgreen')

draw_rect_node(7, 9.2, ['Parallel Evaluation'], facecolor='lightyellow')

draw_rect_node(3, 7.3, ['X/Twitter possibly_sensitive flag', '(weight ×2)'])

draw_rect_node(11, 7.3, ['6 LLMs (GPT-4, Grok, Gemini,', 'LLaMA, DeepSeek, Claude)', '(weight ×1 each)'])

draw_rect_node(7, 5.4, ['Hatebase check', '(flag if match)'])

draw_rect_node(7, 3.8, ['Sum weighted votes', 'total = (X × 2) + Σ(LLMs × 1)'], facecolor='lightgray')

draw_diamond(7, 2.1, ['≥4 votes?'])

draw_diamond(11.2, 2.1, ['Hatebase match', 'AND <3 LLM votes?'])

draw_ellipse_node(11.2, 0.5, ['Review / Flag'], facecolor='lightsalmon')

draw_ellipse_node(3, 0.5, ['Neutral'], facecolor='lightgray')

draw_ellipse_node(7, 0.5, ['Harassment', '(Confidence: ≥6 high,', '4–5 medium)'], facecolor='salmon')

# ────────────────────────────────────────────────
# Arrows

draw_arrow((7, 10.4), (7, 9.8))                       # start → parallel

draw_arrow((7, 8.6), (3, 7.9))                        # parallel → X
draw_arrow((7, 8.6), (11, 7.9))                       # parallel → LLMs
draw_arrow((7, 8.6), (7, 6.1))                        # parallel → Hatebase

draw_arrow((3, 6.6), (7, 4.5))                        # X → sum
draw_arrow((11, 6.6), (7, 4.5))                       # LLMs → sum
draw_arrow((7, 4.7), (7, 4.2))                        # Hatebase → sum

draw_arrow((7, 3.1), (7, 2.7))                        # sum → decision

draw_arrow((7, 1.4), (7, 0.9), label='Yes')           # decision Yes → harass
draw_arrow((7, 1.4), (3, 0.9), label='No')            # decision No → neutral

draw_arrow((7, 1.4), (11.2, 2.1))                     # decision → hatecheck

draw_arrow((11.2, 1.4), (11.2, 0.9), label='Yes')     # hatecheck Yes → review
draw_arrow((11.2, 1.4), (3, 0.9), label='No')         # hatecheck No → neutral

# Title
plt.title('Weighted Ensemble Voting Flowchart for Harassment Classification',
          fontsize=14, pad=35, fontweight='bold')

plt.tight_layout()
# Save for inclusion in paper (uncomment when running locally)
# plt.savefig('ensemble_voting_flowchart.png', dpi=300, bbox_inches='tight')
plt.show()