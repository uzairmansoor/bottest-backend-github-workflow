from src.core.utils import send_slack_alert
from src.models.api_schema import ContactFormRequest


def send_contact_form(request: ContactFormRequest):
    send_slack_alert(
        content=(
            "> :email: *New Contact Form Submission* :email:\n"
            f"First Name: *{request.first_name}*\n"
            f"Last Name: *{request.last_name}*\n"
            f"Company Name: *{request.company_name}*\n"
            f"Business Email: *{request.business_email}*\n"
            f"Message: `{request.message}`\n"
        )
    )

    return {"status": "OK"}
