import os
import secrets
from PIL import Image
from flask import url_for, current_app
import sendgrid
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
from curiosity.config import Config

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/assets/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()

    recipient = user.email # request.form.get('{{user.email.data}}')
    subject = 'Password Reset Request'
    body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''

    # Create the SendGrid client
    sg = sendgrid.SendGridAPIClient(api_key=Config.API_KEY)

    # Create the email message
    message = Mail(
        from_email=Config.EMAIL_SENDER,
        to_emails=[recipient],
        subject=subject,
        plain_text_content=body
    )

    # Send the email
    try:
        response = sg.send(message)
    except HTTPError as e:
        print(e.to_dict)

    if response.status_code == 202:
        return "Email sent successfully!"
    else:
        return "Failed to send email"
