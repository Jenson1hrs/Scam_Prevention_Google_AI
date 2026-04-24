"""Shared page chrome snippets used by the redesigned Streamlit pages."""

from __future__ import annotations

# Shared labels consumed by each page module.
EYEBROW_TOOLS = "SEMA Control Surface"
EYEBROW_ABOUT = "SEMA Blueprint"


def page_header_compact(*, eyebrow: str, title: str, subtitle: str) -> str:
    """Compact, expressive hero strip for inner pages."""
    return f"""
<div class="sema-page-header sema-font" aria-label="Page header">
    <p class="sema-eyebrow">{eyebrow}</p>
    <h1 class="sema-page-title">{title}</h1>
    <p class="sema-page-subtitle">{subtitle}</p>
    <div class="sema-mini-tags" aria-hidden="true">
        <span>Explainable</span>
        <span>Live API</span>
        <span>Malaysia-first</span>
    </div>
</div>
"""


def home_outro() -> str:
    """Closing block shown at the end of the home page."""
    return """
<div class="sema-outro sema-font" aria-label="Next steps">
    <p class="sema-outro-eyebrow">Launch sequence</p>
    <p class="sema-outro-text">
        Pick a workflow from the sidebar and run a live scan. You will get a calibrated risk score,
        narrative explanation, and concrete action guidance in one pass.
    </p>
    <p class="sema-outro-meta">PROJECT 2030 · Track 5 Secure Digital · MyAI Future Hackathon</p>
</div>
"""


def tools_outro() -> str:
    """Small closing strip used on scanner pages."""
    return """
<div class="sema-outro sema-outro--compact sema-font" aria-label="More">
    <p class="sema-outro-text sema-outro-text--compact">
        Need architecture details or deployment notes? Open <strong>About</strong> for the full stack map.
    </p>
</div>
"""


def about_outro() -> str:
    return """
<div class="sema-outro sema-outro--compact sema-font" aria-label="Footer">
    <p class="sema-outro-meta">Built for MyAI Future Hackathon by GDG On Campus UTM</p>
</div>
"""
