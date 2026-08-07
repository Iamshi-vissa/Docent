"""
styles.py - Warm Editorial Claude.ai Single-Theme CSS Generator for Streamlit RAG Chatbot (Docent).
"""

def get_custom_css() -> str:
    """
    Generates a warm, calm, editorial single-theme CSS block inspired by Claude.ai design language.
    Features 'Source Serif 4' headings, 'Inter' body text, terracotta #C15F3C accents, and warm cream #FAF9F5 backgrounds.
    """
    terracotta = "#C15F3C"
    terracotta_hover = "#A34E2F"
    sage_green = "#6B8F71"
    bg_page = "#FAF9F5"
    bg_sidebar = "#F0EEE6"
    bg_card = "#FFFFFF"
    text_primary = "#2D2A26"
    text_secondary = "#6B6559"
    border_color = "#E5E1D8"

    return f"""
    <style id="docent-claude-editorial-theme">
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap');

    /* 1. Warm Editorial Canvas & Typography */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: {bg_page} !important;
        color: {text_primary} !important;
        line-height: 1.65 !important;
    }}

    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    div.block-container, section.main {{
        background-color: {bg_page} !important;
        padding-top: 1.8rem !important;
    }}

    p, span, label, li, a,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] *,
    .stMarkdown, .stMarkdown *, .stText, .stText * {{
        color: {text_primary} !important;
        line-height: 1.65 !important;
    }}

    /* 2. Minimal Warm Sidebar Layout */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarUserContent"],
    div[data-testid="stSidebarNav"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_color} !important;
        padding-top: 1.5rem !important;
    }}

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] * {{
        color: {text_primary} !important;
    }}

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] .stCaption *,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] *,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] span {{
        color: {text_secondary} !important;
        font-weight: 450 !important;
        opacity: 1 !important;
    }}

    /* 3. File Uploader Dropzone & Text Wrapping Fix */
    section[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"],
    [data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}

    div[data-testid="stFileUploaderDropzone"] {{
        background-color: {bg_card} !important;
        border: 1.5px dashed {border_color} !important;
        border-radius: 12px !important;
        padding: 1.4rem 0.8rem !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {terracotta} !important;
        background-color: #FAF4F0 !important;
    }}

    div[data-testid="stFileUploaderDropzoneInstructions"] > div:first-child,
    div[data-testid="stFileUploaderDropzoneInstructions"] > div:first-child * {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    /* Fix text overflow / truncation in sidebar dropzone instructions */
    div[data-testid="stFileUploaderDropzoneInstructions"] small,
    div[data-testid="stFileUploaderDropzoneInstructions"] small *,
    section[data-testid="stFileUploader"] small,
    section[data-testid="stFileUploader"] small * {{
        color: {text_secondary} !important;
        font-size: 0.78rem !important;
        font-weight: 450 !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.35 !important;
    }}

    div[data-testid="stFileUploaderDropzone"] svg,
    div[data-testid="stFileUploaderDropzone"] svg * {{
        fill: {terracotta} !important;
        color: {terracotta} !important;
    }}

    /* 4. Expander & Popover Components */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary,
    .st-emotion-cache summary,
    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] details summary * {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary svg path,
    div[data-testid="stExpander"] details summary svg,
    div[data-testid="stExpander"] details summary svg * {{
        fill: {terracotta} !important;
        color: {terracotta} !important;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        background-color: {bg_card} !important;
        box-shadow: none !important;
    }}

    div[data-testid="stPopover"] button {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        color: {text_primary} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stPopover"] button:hover {{
        border-color: {terracotta} !important;
        color: {terracotta} !important;
        background-color: #FAF4F0 !important;
    }}

    /* 5. Chat Message System (Claude Editorial Quote Block Style) */
    div[data-testid="stChatMessage"] {{
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }}

    div[data-testid="stChatMessage"] .stChatMessageContent {{
        border-radius: 12px !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        box-shadow: none !important;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
    div[data-testid="stChatMessage"] .stChatMessageContent * {{
        color: {text_primary} !important;
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]),
    div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageUserIcon"]) {{
        flex-direction: row-reverse !important;
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stChatMessageContent,
    div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageUserIcon"]) .stChatMessageContent {{
        background-color: {bg_sidebar} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        box-shadow: none !important;
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stChatMessageContent [data-testid="stMarkdownContainer"] *,
    div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageUserIcon"]) .stChatMessageContent [data-testid="stMarkdownContainer"] * {{
        color: {text_primary} !important;
    }}

    /* 6. Chunk Snippet Cards */
    .chunk-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-left: 4px solid {terracotta};
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
    }}

    .chunk-snippet {{
        font-family: monospace;
        font-size: 0.83rem;
        color: {text_primary} !important;
        background-color: {bg_sidebar} !important;
        padding: 0.65rem 0.85rem;
        border-radius: 6px;
        white-space: pre-wrap;
        word-break: break-word;
        border: 1px solid {border_color} !important;
        line-height: 1.5;
    }}

    /* 7. Header Hero Section (Docent Editorial Title) */
    .hero-accent-bar {{
        height: 2px;
        width: 100%;
        background-color: {terracotta};
        margin-bottom: 1.2rem;
    }}

    .app-header-title {{
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-size: 2.3rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: {text_primary} !important;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}

    .app-header-title .terracotta-dot {{
        color: {terracotta};
    }}

    .app-header-subtitle {{
        font-size: 0.95rem;
        color: {text_secondary} !important;
        margin-bottom: 1.2rem;
    }}

    /* 8. Buttons */
    div.stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }}

    div.stButton > button:hover {{
        border-color: {terracotta} !important;
        color: {terracotta} !important;
        background-color: #FAF4F0 !important;
    }}

    div.stButton > button[kind="primary"] {{
        background-color: {terracotta} !important;
        color: #FFFFFF !important;
        border: none !important;
    }}

    div.stButton > button[kind="primary"]:hover {{
        background-color: {terracotta_hover} !important;
        color: #FFFFFF !important;
    }}

    /* 9. Chat Input Field */
    div[data-testid="stChatInput"] {{
        border: 1.5px solid {border_color} !important;
        border-radius: 16px !important;
        background-color: {bg_card} !important;
        box-shadow: none !important;
    }}

    div[data-testid="stChatInput"]:focus-within {{
        border-color: {terracotta} !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        color: {text_primary} !important;
        background-color: transparent !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder,
    div[data-testid="stChatInput"] textarea::-webkit-input-placeholder,
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {text_secondary} !important;
        opacity: 1 !important;
    }}

    /* Badges */
    .badge-terracotta {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #FFFFFF !important;
        background-color: {terracotta};
    }}

    .badge-sage {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #FFFFFF !important;
        background-color: {sage_green};
    }}

    .empty-state-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }}

    .empty-state-title {{
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-size: 1.5rem;
        font-weight: 600;
        color: {text_primary} !important;
        margin-bottom: 0.5rem;
    }}

    .empty-state-desc {{
        font-size: 0.95rem;
        color: {text_secondary} !important;
        max-width: 540px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
    }}

    .step-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1.2rem;
        margin-top: 1.5rem;
    }}

    .step-card {{
        background-color: {bg_page};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1.2rem;
    }}

    .step-num {{
        display: inline-block;
        width: 26px;
        height: 26px;
        background-color: {terracotta};
        color: #FFFFFF !important;
        border-radius: 50%;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        line-height: 26px;
        margin-bottom: 0.6rem;
    }}

    .step-title {{
        font-weight: 600;
        font-size: 0.92rem;
        color: {text_primary} !important;
        margin-bottom: 0.3rem;
    }}

    .step-text {{
        font-size: 0.82rem;
        color: {text_secondary} !important;
        line-height: 1.45;
    }}
    </style>
    """
