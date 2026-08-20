"""Branded HTML shell + helpers for portfolio transactional emails."""

PORTFOLIO_URL = "https://gauravsingh.dev"
BRAND_NAME = "Gaurav Singh"
BRAND_TAGLINE = "AI Engineer · GenAI · Backend"

COLORS = {
    "bg": "#F7F5F0",
    "surface": "#FFFFFF",
    "text": "#111525",
    "muted": "#596174",
    "accent": "#E8872A",
    "accent_soft": "#FFF4E8",
    "border": "#E7E8EF",
}


def _var(name: str) -> str:
    return "{{ " + name + " }}"


def email_shell(
    *,
    eyebrow: str,
    headline: str,
    body_html: str,
    footer_note: str = "You're receiving this because you interacted with my portfolio.",
) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{headline}</title>
</head>
<body style="margin:0;padding:0;background-color:{COLORS['bg']};font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:{COLORS['text']};">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:{COLORS['bg']};padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background-color:{COLORS['surface']};border:1px solid {COLORS['border']};border-radius:20px;overflow:hidden;box-shadow:0 12px 40px rgba(17,21,37,0.08);">
          <tr>
            <td style="padding:28px 32px 20px;background:linear-gradient(135deg,{COLORS['accent_soft']} 0%,{COLORS['surface']} 70%);border-bottom:1px solid {COLORS['border']};">
              <p style="margin:0 0 8px;font-size:11px;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;color:{COLORS['accent']};">{eyebrow}</p>
              <h1 style="margin:0;font-size:24px;line-height:1.25;font-weight:700;color:{COLORS['text']};">{headline}</h1>
              <p style="margin:10px 0 0;font-size:13px;color:{COLORS['muted']};">{BRAND_NAME} · {BRAND_TAGLINE}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 32px;font-size:15px;line-height:1.65;color:{COLORS['text']};">
              {body_html}
            </td>
          </tr>
          <tr>
            <td style="padding:20px 32px 28px;border-top:1px solid {COLORS['border']};background-color:{COLORS['bg']};">
              <p style="margin:0 0 8px;font-size:12px;line-height:1.6;color:{COLORS['muted']};">{footer_note}</p>
              <p style="margin:0;font-size:12px;color:{COLORS['muted']};">
                <a href="{PORTFOLIO_URL}" style="color:{COLORS['accent']};text-decoration:none;font-weight:600;">Visit portfolio</a>
                &nbsp;·&nbsp; {BRAND_NAME}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def info_row(label: str, var_name: str) -> str:
    value = _var(var_name)
    return f"""
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:0 0 10px;">
  <tr>
    <td style="padding:10px 14px;background-color:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:12px;">
      <p style="margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{COLORS['muted']};">{label}</p>
      <p style="margin:0;font-size:14px;color:{COLORS['text']};word-break:break-word;">{value}</p>
    </td>
  </tr>
</table>"""


def message_block(var_name: str = "message") -> str:
    value = _var(var_name)
    return f"""
<div style="margin-top:16px;padding:16px 18px;background-color:{COLORS['bg']};border:1px solid {COLORS['border']};border-radius:14px;">
  <p style="margin:0 0 8px;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{COLORS['muted']};">Message</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:{COLORS['text']};white-space:pre-wrap;">{value}</p>
</div>"""


def otp_block() -> str:
    return f"""
<div style="margin:24px 0;text-align:center;padding:24px 16px;background-color:{COLORS['accent_soft']};border:1px dashed {COLORS['accent']};border-radius:16px;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:{COLORS['muted']};">Your verification code</p>
  <p style="margin:0;font-size:36px;font-weight:800;letter-spacing:0.35em;color:{COLORS['accent']};font-family:Consolas,Monaco,monospace;">{_var('otp')}</p>
</div>"""


def mailto_button(label: str, email_var: str = "email") -> str:
    href = "mailto:" + _var(email_var)
    return f"""
<p style="margin:20px 0 0;">
  <a href="{href}" style="display:inline-block;padding:12px 20px;background-color:{COLORS['accent']};color:#FFFFFF;text-decoration:none;border-radius:999px;font-size:14px;font-weight:600;">{label}</a>
</p>"""
