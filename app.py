from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Chit_Fund_Records').sheet1


def add_payment(name, month, amount, paid):
    sheet.append_row([name, month, str(amount), paid])


@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower().strip()
    resp = MessagingResponse()

    if incoming_msg in ["1", "add"]:
        resp.message("Please enter like:\nRam July 5000 yes")
    elif incoming_msg in ["2", "pending"]:
        resp.message("Please type:\npending July")
    elif incoming_msg in ["3", "paid"]:
        resp.message("Please type:\npaid July")
    elif len(incoming_msg.split()) == 4:
        name, month, amount, paid = incoming_msg.split()
        add_payment(name.capitalize(), month.capitalize(), amount, paid.lower())
        resp.message(f"✅ Payment added for {name} for {month}.")
    elif incoming_msg.startswith('pending'):
        _, month = incoming_msg.split()
        records = sheet.get_all_records()
        pending = [rec for rec in records if rec["Month"].lower() == month.lower() and rec["Paid?"].lower() == "no"]
        if pending:
            msg = "\n".join([f"{rec['Name']} hasn't paid {rec['Amount']} for {month.capitalize()}" for rec in pending])
        else:
            msg = f"🎉 No pending payments for {month.capitalize()}!"
        resp.message(msg)
    elif incoming_msg.startswith('paid'):
        _, month = incoming_msg.split()
        records = sheet.get_all_records()
        paid = [rec for rec in records if rec["Month"].lower() == month.lower() and rec["Paid?"].lower() == "yes"]
        if paid:
            msg = "\n".join([f"{rec['Name']} paid {rec['Amount']} for {month.capitalize()}" for rec in paid])
        else:
            msg = f"No payments found for {month.capitalize()}."
        resp.message(msg)
    else:
        resp.message(
            "👋 Hi Aunty! Welcome to ChitBot:\n\n"
            "Reply with:\n"
            "1️⃣ ✅ Add Payment\n"
            "2️⃣ ❗ Show Pending\n"
            "3️⃣ 💰 Show Paid\n"
            "4️⃣ 📊 Monthly Summary (coming soon)\n"
            "5️⃣ 🔐 Backup Data (coming soon)"
        )
    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
