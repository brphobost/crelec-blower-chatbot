# Email Configuration Guide for Crelec Blower Chatbot

## Option 1: Gmail (Recommended for Quick Setup)

### Step 1: Gmail Account Setup
1. Use an existing Gmail account or create a new one (e.g., noreply.crelec@gmail.com)
2. Enable 2-Factor Authentication:
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification" and follow the steps

3. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" from dropdown
   - Click "Generate"
   - Copy the 16-character password (looks like: xxxx xxxx xxxx xxxx)

### Step 2: Update Environment Variables
Create a `.env` file in your project root:

```env
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password-here
EMAIL_FROM=noreply.crelec@gmail.com
ADMIN_EMAIL=crelec@live.co.za
```

### Step 3: Update api/send_email.py
Replace the email sending section with:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Inside the do_POST method, replace the comment block with:
# Configure SMTP
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))

# Send the email
server.send_message(msg)
server.quit()
```

---

## Option 2: SendGrid (Professional Solution)

### Step 1: SendGrid Account
1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Verify your email domain
3. Create API Key:
   - Settings → API Keys → Create API Key
   - Select "Full Access"
   - Copy the key

### Step 2: Install SendGrid
```bash
pip install sendgrid
```

### Step 3: Update api/send_email.py
```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType

# Replace SMTP section with:
message = Mail(
    from_email='noreply@crelec.co.za',
    to_emails=to_email,
    subject=f'Crelec Blower Quote #{quote_id}',
    html_content=body
)

# Add PDF attachment
if pdf_base64:
    attachment = Attachment(
        FileContent(pdf_base64),
        FileName(f'Crelec_Quote_{quote_id}.pdf'),
        FileType('application/pdf')
    )
    message.attachment = attachment

# Send
sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
response = sg.send(message)
```

---

## Option 3: Resend (Modern & Developer-Friendly)

### Step 1: Resend Account
1. Sign up at https://resend.com (free tier: 100 emails/day)
2. Add and verify your domain
3. Get API key from dashboard

### Step 2: Install Resend
```bash
pip install resend
```

### Step 3: Update api/send_email.py
```python
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

# Send email
params = {
    "from": "Crelec <noreply@crelec.co.za>",
    "to": [to_email],
    "cc": ["crelec@live.co.za"],
    "subject": f"Crelec Blower Quote #{quote_id}",
    "html": body,
    "attachments": [
        {
            "filename": f"Crelec_Quote_{quote_id}.pdf",
            "content": pdf_base64
        }
    ]
}

email = resend.Emails.send(params)
```

---

## Option 4: EmailJS (Client-Side Only)

### Step 1: EmailJS Account
1. Sign up at https://www.emailjs.com (free: 200 emails/month)
2. Add email service (Gmail/Outlook)
3. Create email template
4. Get credentials:
   - Service ID
   - Template ID
   - Public Key

### Step 2: Update frontend/quote-generator.js
```javascript
// Replace YOUR_PUBLIC_KEY with actual key
emailjs.init("your_actual_public_key_here");

// In sendQuoteEmail method:
const response = await emailjs.send(
    'your_service_id',
    'your_template_id',
    templateParams
);
```

---

## Environment Variables on Vercel

After choosing your email service:

1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Add your variables:
   - `EMAIL_USER`
   - `EMAIL_PASS`
   - `ADMIN_EMAIL`
   etc.

5. Redeploy for changes to take effect

---

## Testing Your Email Setup

1. Test locally first:
```bash
python api/send_email.py
```

2. Use a test endpoint:
```bash
curl -X POST http://localhost:3000/api/send_email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"test@example.com", "quote_id":"TEST123"}'
```

3. Check spam folder if emails don't arrive

---

## Recommended Setup for Crelec

For Crelec, I recommend:

1. **Quick Start**: Gmail with App Password
2. **Professional**: SendGrid (better deliverability, analytics)
3. **Modern**: Resend (great developer experience)

The Gmail option is fastest to set up and free for your volume.