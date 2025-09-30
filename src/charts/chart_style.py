# Centralized Matplotlib styling for all charts
# This avoids referencing fonts that may not exist on headless/Linux servers
# and prevents repeated rcParams mutations + findfont warnings.

import matplotlib

_APPLIED = False

def apply_chart_style(force: bool = False):
    """Apply central Matplotlib style.

    Parameters:
        force: if True re-apply even if previously applied (useful after modifying this module).
    """
    global _APPLIED
    if _APPLIED and not force:
        return
    matplotlib.rcParams.update({
        # Keep it to fonts that are bundled with matplotlib to avoid findfont warnings.
        "font.family": "DejaVu Sans",
        "font.sans-serif": [
            "DejaVu Sans",
            "sans-serif"
        ],
        # Ensure minus signs render correctly
        "axes.unicode_minus": False,
    })
    _APPLIED = True
