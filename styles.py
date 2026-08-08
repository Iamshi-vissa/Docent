"""
styles.py - Single fixed warm/calm theme for Docent.
No dark mode, no toggle -- one consistent palette everywhere.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@500;600&display=swap');

:root {
    --page-bg: #FAF9F5;
    --sidebar-bg: #F0EEE6;
    --card-bg: #FFFFFF;
    --text-primary: #2D2A26;
    --text-secondary: #6B6559;
    --border-color: #E5E1D8;
    --accent: #C15F3C;
    --accent-hover: #A34E2F;
    --accent-tint: #F5E6DE;
    --sage: #6B8F71;
    --sage-tint: #E7EFE8;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: var(--page-bg) !important;
    color: var(--text-primary) !important;
}

div.block-container, section.main {
    background-color: var(--page-bg) !important;
}

p, span, label, li, a,
div[data-testid="stMarkdownContainer"], div[data-testid="stMarkdownContainer"] * {
    color: var(--text-primary) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-color) !important;
    z-index: 100 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    max-height: 100vh !important;
    overflow-y: auto !important;
}
.sidebar-heading {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] * {
    color: var(--text-primary) !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: var(--text-secondary) !important;
    opacity: 1 !important;
}

/* Header */
.docent-header {
    padding-top: 0.5rem;
    margin-bottom: 1.5rem;
}
.docent-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}
.docent-title .accent-dot {
    color: var(--accent);
}
.docent-tagline {
    font-size: 1rem;
    color: var(--text-secondary) !important;
}
.docent-accent-bar {
    height: 3px;
    width: 64px;
    background-color: var(--accent);
    border-radius: 2px;
    margin: 0.6rem 0 1rem 0;
}

/* Popover / info content */
div[data-testid="stPopoverBody"] {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
}
div[data-testid="stPopoverBody"] * {
    color: var(--text-primary) !important;
}

/* File uploader */
div[data-testid="stFileUploaderDropzone"] {
    background-color: var(--card-bg) !important;
    border: 1.5px dashed var(--border-color) !important;
    border-radius: 10px !important;
    padding: 1.2rem 1rem !important;
}
div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] div,
[data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stFileUploader"] label,
section[data-testid="stFileUploader"] label * {
    color: var(--text-primary) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stFileUploader"] small {
    color: var(--text-secondary) !important;
    opacity: 1 !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}
[data-testid="stFileUploaderFile"], div[data-testid="stFileUploaderFileData"] {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
}
[data-testid="stFileUploaderFile"] * {
    color: var(--text-primary) !important;
}

/* Uploaded document list (custom) */
.doc-list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.85rem;
}
.doc-list-name {
    color: var(--text-primary) !important;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 70%;
}
.doc-list-count {
    color: var(--text-secondary) !important;
    font-size: 0.78rem;
}

/* Chat bubbles */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
}
div[data-testid="stChatMessage"] .stChatMessageContent {
    border-radius: 12px !important;
    padding: 0.8rem 1.1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    background-color: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
    color: var(--text-primary) !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stChatMessageContent {
    background-color: var(--sidebar-bg) !important;
    border: 1px solid var(--border-color) !important;
}

/* Citation tags inline */
.citation-tag {
    display: inline-block;
    background-color: var(--accent-tint);
    color: var(--accent-hover) !important;
    font-size: 0.78rem;
    padding: 1px 6px;
    border-radius: 4px;
    margin: 0 1px;
}

/* Retrieved chunks expander */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary svg { fill: var(--text-primary) !important; }
div[data-testid="stExpander"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    background-color: var(--card-bg) !important;
}
.chunk-card {
    background-color: var(--page-bg);
    border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.6rem;
    font-size: 0.85rem;
}
.chunk-meta {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 0.4rem;
}
.chunk-badge {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;
}
.chunk-badge.page { background-color: var(--accent-tint); color: var(--accent-hover); }
.chunk-badge.score { background-color: var(--sage-tint); color: var(--sage); }

/* Buttons */
div.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    background-color: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}
div.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
div.stButton > button[kind="primary"] {
    background-color: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: var(--accent-hover) !important;
}
div[data-testid="stDownloadButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    background-color: var(--card-bg) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
}

/* Chat input */
div[data-testid="stChatInput"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 18px !important;
    background-color: var(--card-bg) !important;
}
div[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    background-color: transparent !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-secondary) !important;
    opacity: 1 !important;
}

/* Empty state */
.empty-state-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 2.2rem 2rem;
    text-align: center;
    margin: 1.2rem 0;
}
.empty-state-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem;
}
.empty-state-desc {
    font-size: 0.92rem;
    color: var(--text-secondary) !important;
    max-width: 520px;
    margin: 0 auto 1.5rem auto;
    line-height: 1.6;
}
.step-card {
    background-color: var(--page-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1rem;
    text-align: left;
}
.step-num {
    display: inline-block;
    width: 22px;
    height: 22px;
    background-color: var(--accent);
    color: #FFFFFF !important;
    border-radius: 50%;
    text-align: center;
    font-weight: 700;
    font-size: 0.75rem;
    line-height: 22px;
    margin-bottom: 0.5rem;
}
.step-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-primary) !important;
    margin-bottom: 0.2rem;
}
.step-text {
    font-size: 0.8rem;
    color: var(--text-secondary) !important;
}
</style>
"""


def get_custom_css() -> str:
    return CUSTOM_CSS
