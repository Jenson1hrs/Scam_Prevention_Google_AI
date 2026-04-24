"""About page for the redesigned frontend."""

from __future__ import annotations

import streamlit as st

from src.frontend._pages._layout import EYEBROW_ABOUT, about_outro, page_header_compact


def render() -> None:
    st.markdown(
        page_header_compact(
            eyebrow=EYEBROW_ABOUT,
            title="About The SEMA System",
            subtitle=(
                "Scam Explainer & Mitigation Agent: an explainable fraud intelligence stack "
                "for Malaysian scam contexts, designed for PROJECT 2030 Track 5."
            ),
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="sema-about sema-font">
<p class="sema-prose">
    <strong>SEMA</strong> is built around one principle: risk systems must be legible.
    Instead of returning a bare score, it returns evidence, context, and mitigation steps.
</p>

<h3 class="sema-h2">Threat landscape</h3>
<p class="sema-prose">
    Digital fraud continuously mutates across social engineering channels.
    SEMA emphasizes high-frequency scam patterns observed in Malaysia:
</p>
<ul>
    <li><strong>Authority impersonation</strong>: fake police, bank, or regulator directives</li>
    <li><strong>Urgency extraction</strong>: countdown pressure to force immediate transfer</li>
    <li><strong>Platform mimicry</strong>: spoofed courier, wallet, and marketplace notices</li>
    <li><strong>Fee-before-release traps</strong>: fake customs, tax, or verification fees</li>
    <li><strong>Credential phishing</strong>: malicious links masked as account recovery</li>
</ul>

<h3 class="sema-h2">Multi-agent architecture</h3>
<p class="sema-prose">
    Three specialist agents run in parallel and feed a weighted orchestrator layer.
</p>
<div class="sema-table-wrap">
<table class="sema-table">
<thead>
<tr><th>Agent</th><th>What It Sees</th><th>Output</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>ML Agent</strong></td>
    <td>Numerical transaction features and behavioral indicators</td>
    <td>Baseline fraud probability + explainability cues</td>
</tr>
<tr>
    <td><strong>Pattern Agent</strong></td>
    <td>Language, intent, and scam archetype similarity</td>
    <td>Pattern-aligned risk signal + scam category</td>
</tr>
<tr>
    <td><strong>Context Agent</strong></td>
    <td>Temporal, device, and user-behavior context</td>
    <td>Contextual risk modifiers and suspicious signals</td>
</tr>
<tr>
    <td><strong>Orchestrator</strong></td>
    <td>All agent signals + fallback logic</td>
    <td>Final risk score, level, and action recommendation</td>
</tr>
</tbody>
</table>
</div>
<p class="sema-prose">
    For <strong>message analysis</strong>, Gemini scans SMS / WhatsApp-style text for phishing links,
    urgency, impersonation, and red flags aligned to local scams.
</p>

<h3 class="sema-h2">Technology stack</h3>
<div class="sema-table-wrap">
<table class="sema-table">
<thead>
<tr><th>Layer</th><th>Implementation</th></tr>
</thead>
<tbody>
<tr><td><strong>LLM reasoning</strong></td><td>Google Gemini via <code>google-genai</code></td></tr>
<tr><td><strong>ML</strong></td><td>XGBoost + scikit-learn pipeline</td></tr>
<tr><td><strong>API</strong></td><td>FastAPI (Python)</td></tr>
<tr><td><strong>UI</strong></td><td>Streamlit</td></tr>
<tr><td><strong>Deploy</strong></td><td>Docker → Google Cloud Run</td></tr>
<tr><td><strong>Explainability</strong></td><td>SHAP (TreeExplainer)</td></tr>
</tbody>
</table>
</div>

<h3 class="sema-h2">Project alignment</h3>
<p class="sema-prose"><strong>PROJECT 2030 - Track 5: Secure Digital (FinTech &amp; Security)</strong></p>
<blockquote>
    Digital fraud evolves faster than static defenses. A resilient digital economy needs
    adaptive, real-time, and explainable protection layers that users can trust.
</blockquote>
<p class="sema-prose">
    SEMA addresses this with a layered, explainable intelligence loop instead of brittle
    rule-only blocking.
</p>

<h3 class="sema-h2">Team and disclosure</h3>
<p class="sema-prose">
    Built for the <strong>MyAI Future Hackathon</strong> by <strong>GDG On Campus UTM</strong>.
    AI-assisted tooling was used during development and disclosed according to hackathon rules.
</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(about_outro(), unsafe_allow_html=True)
