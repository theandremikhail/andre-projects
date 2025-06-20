from reader import authenticate_gmail, read_unread_emails
from reader import send_email
from chatgpt import generate_reply

if __name__ == '__main__':
    service = authenticate_gmail()
    unread_emails = read_unread_emails(service)
    your_name = "Andre Mikhail Serra"

    for email in unread_emails:
        print("\n" + "-"*60)
        prompt = f"""You received the following email from {email['from']} with subject "{email['subject']}":

    {email['body']}

    Write a professional reply. But do not include "Here is a professional response to the email:" this in the reply. Just proceed with the email.
    End the email with:
    Best regards,
    {your_name}"""
        reply = generate_reply(prompt)

        print(f"Original: {email['body']}")
        print(f"{reply}")

        # OPTIONAL: Ask before sending
        should_send = input("Send this reply? (y/n): ").lower()
        if should_send == 'y':
            send_email(
            service,
            to=email['from'],
            subject=f"Re: {email['subject']}",
            body=reply,
            thread_id=email.get('threadId'),
            in_reply_to=email.get('messageId'),
            references=email.get('messageId')
            )
        else:
            print("Skipped sending.")
