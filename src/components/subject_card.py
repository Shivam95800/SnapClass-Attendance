import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    stats_html = ""
    if stats:
        chips = []
        for icon, label, value in stats:
            chips.append(f"""
                <div style="flex: 1 1 45%; min-width: 120px; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 12px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.15rem;">{icon}</span>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">{label}</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{value}</div>
                    </div>
                </div>
            """)
        stats_html = f"""
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0 14px 0;">
                {"".join(chips)}
            </div>
        """

    html = f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 22px; margin-bottom: 18px; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05); transition: all 0.2s ease;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
                <div>
                    <h3 style="margin: 0; color: #0F172A; font-size: 1.35rem; font-weight: 700; line-height: 1.25;">{name}</h3>
                </div>
                <div style="display: flex; gap: 6px; flex-shrink: 0;">
                    <span style="background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">{code}</span>
                    <span style="background: #FDF2F8; color: #DB2777; border: 1px solid #FBCFE8; font-size: 0.78rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">Sec {section}</span>
                </div>
            </div>
            {stats_html}
        </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
