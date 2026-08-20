"""Default email templates seeded into the CMS."""

from app.modules.email_template.layouts import (
    email_shell,
    info_row,
    mailto_button,
    message_block,
    otp_block,
)

DEFAULT_EMAIL_TEMPLATES: list[dict] = [
    {
        "name": "Email verification OTP",
        "slug": "email_otp",
        "subject": "{{ otp }} is your verification code",
        "html_body": email_shell(
            eyebrow="Security",
            headline="Verify your email",
            body_html="""
<p style="margin:0 0 12px;">Hi,</p>
<p style="margin:0 0 8px;">Use the code below to verify your email address on my portfolio. This helps keep contact and booking requests secure.</p>
""" + otp_block() + """
<p style="margin:0;font-size:13px;color:#596174;">This code expires in <strong>10 minutes</strong>. If you didn't request it, you can safely ignore this email.</p>
""",
            footer_note="Verification email · Do not share this code with anyone.",
        ),
        "text_body": """Hi,

Your verification code: {{ otp }}

This code expires in 10 minutes. If you didn't request it, ignore this email.

— Gaurav Singh
""",
        "variables": ["email", "otp", "purpose"],
    },
    {
        "name": "Contact — admin notification",
        "slug": "contact_admin_notify",
        "subject": "New contact: {{ subject }}",
        "html_body": email_shell(
            eyebrow="Inbox",
            headline="New contact message",
            body_html="""
<p style="margin:0 0 16px;">Someone submitted your portfolio contact form.</p>
"""
            + info_row("Name", "name")
            + info_row("Email", "email")
            + info_row("Subject", "subject")
            + message_block("message")
            + mailto_button("Reply via email", "email"),
            footer_note="Admin notification from your portfolio contact form.",
        ),
        "text_body": """New contact message

Name: {{ name }}
Email: {{ email }}
Subject: {{ subject }}

Message:
{{ message }}
""",
        "variables": ["name", "email", "subject", "message"],
    },
    {
        "name": "Contact — user acknowledgment",
        "slug": "contact_user_ack",
        "subject": "Got your message — {{ subject }}",
        "html_body": email_shell(
            eyebrow="Inbox",
            headline="Thanks for reaching out",
            body_html="""
<p style="margin:0 0 12px;">Hi {{ name }},</p>
<p style="margin:0 0 12px;">I received your message about <strong>{{ subject }}</strong>. I'll review it and get back to you within 12 hours on business days.</p>
<p style="margin:0;padding:14px 16px;background-color:#F7F5F0;border-radius:12px;font-size:14px;color:#596174;">If your request is urgent, feel free to reply to this email directly.</p>
<p style="margin:20px 0 0;">— Gaurav Singh</p>
""",
            footer_note="Confirmation that your contact form submission was received.",
        ),
        "text_body": """Hi {{ name }},

Thanks for reaching out. I received your message about "{{ subject }}" and will get back to you soon.

— Gaurav Singh
""",
        "variables": ["name", "email", "subject", "message"],
    },
    {
        "name": "Contact reply",
        "slug": "contact_reply",
        "subject": "Re: {{ subject }}",
        "html_body": email_shell(
            eyebrow="Reply",
            headline="Message from Gaurav",
            body_html="""
<p style="margin:0 0 12px;">Hi {{ name }},</p>
"""
            + message_block("message")
            + """
<p style="margin:20px 0 0;">— Gaurav Singh<br/><span style="font-size:13px;color:#596174;">AI Engineer · GenAI · Backend</span></p>
""",
            footer_note="Reply to your contact form message.",
        ),
        "text_body": """Hi {{ name }},

{{ message }}

— Gaurav Singh
""",
        "variables": ["name", "email", "subject", "message"],
    },
    {
        "name": "Feedback — admin notification",
        "slug": "feedback_admin_notify",
        "subject": "New feedback from {{ name }}",
        "html_body": email_shell(
            eyebrow="Testimonials",
            headline="New feedback submitted",
            body_html="""
<p style="margin:0 0 16px;">A visitor shared feedback on your portfolio. Review it in Admin → Testimonials to approve or reject.</p>
"""
            + info_row("Name", "name")
            + info_row("Email", "email")
            + info_row("LinkedIn", "linkedin_url")
            + message_block("message"),
            footer_note="Admin notification · Pending testimonial review.",
        ),
        "text_body": """New feedback submitted

Name: {{ name }}
Email: {{ email }}
LinkedIn: {{ linkedin_url }}

Message:
{{ message }}
""",
        "variables": ["name", "email", "linkedin_url", "message"],
    },
    {
        "name": "Feedback — user acknowledgment",
        "slug": "feedback_user_ack",
        "subject": "Thanks for your feedback, {{ name }}",
        "html_body": email_shell(
            eyebrow="Testimonials",
            headline="Thank you for sharing",
            body_html="""
<p style="margin:0 0 12px;">Hi {{ name }},</p>
<p style="margin:0 0 12px;">Thank you for taking the time to share your feedback. I really appreciate it.</p>
<p style="margin:0 0 12px;">I'll review your testimonial and publish it on my portfolio once approved.</p>
<p style="margin:20px 0 0;">— Gaurav Singh</p>
""",
            footer_note="Confirmation that your feedback was received.",
        ),
        "text_body": """Hi {{ name }},

Thank you for sharing your feedback. I'll review it before publishing on my portfolio.

— Gaurav Singh
""",
        "variables": ["name", "message"],
    },
    {
        "name": "Service booking — user confirmation",
        "slug": "service_booking_user",
        "subject": "Booking received: {{ service_name }}",
        "html_body": email_shell(
            eyebrow="Services",
            headline="Booking request confirmed",
            body_html="""
<p style="margin:0 0 12px;">Hi {{ name }},</p>
<p style="margin:0 0 16px;">Your booking request for <strong>{{ service_name }}</strong> has been received. I'll review the details and follow up shortly.</p>
"""
            + info_row("Service", "service_name")
            + message_block("message")
            + """
<p style="margin:20px 0 0;">— Gaurav Singh</p>
""",
            footer_note="Confirmation of your service booking request.",
        ),
        "text_body": """Hi {{ name }},

Your booking request for "{{ service_name }}" has been received.

Details:
{{ message }}

I'll get back to you shortly.

— Gaurav Singh
""",
        "variables": ["name", "email", "service_name", "subject", "message"],
    },
    {
        "name": "Service booking — admin notification",
        "slug": "service_booking_admin",
        "subject": "New booking: {{ service_name }}",
        "html_body": email_shell(
            eyebrow="Services",
            headline="New service booking",
            body_html="""
<p style="margin:0 0 16px;">A visitor booked a service on your portfolio.</p>
"""
            + info_row("Service", "service_name")
            + info_row("Name", "name")
            + info_row("Email", "email")
            + message_block("message")
            + mailto_button("Email client", "email"),
            footer_note="Admin notification from service booking form.",
        ),
        "text_body": """New service booking

Service: {{ service_name }}
Name: {{ name }}
Email: {{ email }}

Details:
{{ message }}
""",
        "variables": ["name", "email", "service_name", "subject", "message"],
    },
]
