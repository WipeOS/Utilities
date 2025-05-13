from bottle import route, run, request, response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging

logging.basicConfig(filename='email_logger.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
email_logger = logging.getLogger('email_logger')
# Email configuration
EMAIL_ADDRESS = "alerts@wipeos.com"
EMAIL_PASSWORD = "cqln bfzc zjrc pezk"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_PORT = 17771

@route('/up')
def is_up():
    return {'status': 'up'}
@route('/send_email', method='POST')
def send_email():
    try:
        data = request.json
        recipient_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        mimetext = data.get('mimetype', 'text/plain')

        if not all([recipient_email, subject, body]):
            response.status = 400
            return {'error': 'Missing required fields'}

        message = MIMEMultipart()
        message['From'] = EMAIL_ADDRESS
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, mimetext)) # change to html if contains html?

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)

        email_logger.info("SUCCESS: {}".format(data))
        return {'message': 'Email sent successfully'}

    except json.JSONDecodeError:
        response.status = 400
        email_logger.error("Invalid JSON format")
        email_logger.info("FAILURE: {}".format(data))
        return {'error': 'Invalid JSON format'}
    except Exception as e:
        response.status = 500
        email_logger.error("An error occurred: {}".format(str(e)))
        email_logger.info("FAILURE: {}".format(data))
        return {'error': f'An error occurred: {str(e)}'}

if __name__ == '__main__':
    run(host='0.0.0.0', port=EMAIL_PORT, debug=False, quiet=True)

