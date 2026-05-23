from alerts.elevenlabs_service import generate_message
from alerts.twilio_service import send_whatsapp_message


def check_unsolved_users():
    users = [{"name": "Vansh", "phone": "+917819834452", "solved_today": False}]

    for user in users:
        if not user["solved_today"]:
            message = generate_message(user["name"])

            print("Triggering alert for:", user["name"])
            print(message)
            try:
                send_whatsapp_message(user["phone"], message)
                print(f"WhatsApp message sent successfully to {user['phone']}!")
            except Exception as e:
                print(f"Failed to send WhatsApp message to {user['phone']}:", e)
