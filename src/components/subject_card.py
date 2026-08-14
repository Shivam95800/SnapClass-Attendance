import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    stats_chips = ""
    if stats:
        chips = []
        for icon, label, value in stats:
            chips.append(
                f'<div style="flex: 1 1 45%; min-width: 110px; background: #F8FAFC; border: 1px solid #E2E8F0; '
                f'padding: 10px 14px; border-radius: 12px; display: flex; align-items: center; gap: 8px;">'
                f'<span style="font-size: 1.1rem;">{icon}</span>'
                f'<div>'
                f'<div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">{label}</div>'
                f'<div style="font-size: 1.05rem; font-weight: 700; color: #0F172A;">{value}</div>'
                f'</div></div>'
            )
        stats_chips = (
            '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0 10px 0;">'
            + "".join(chips)
            + "</div>"
        )

    card_html = (
        '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; '
        'padding: 22px; margin-bottom: 4px; box-shadow: 0 4px 16px -2px rgba(15,23,42,0.06);">'
        '<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">'
        '<h3 style="margin: 0; color: #0F172A; font-size: 1.25rem; font-weight: 700; line-height: 1.3;">'
        + name +
        '</h3>'
        '<div style="display: flex; gap: 6px; flex-shrink: 0;">'
        '<span style="background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; '
        'font-family: monospace; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">'
        + code +
        '</span>'
        '<span style="background: #FDF2F8; color: #DB2777; border: 1px solid #FBCFE8; '
        'font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">Sec '
        + section +
        '</span>'
        '</div>'
        '</div>'
        + stats_chips +
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
