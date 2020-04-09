import pandas as pd
import time
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db_init import conn
from settings import RECIPIENT_EMAILS, RECIPIENT_NAMES, API_KEY, PORT


def get_apartment_data():
    query = """SELECT * from prices
    left join apartment on apartment.rowid = prices.apartment_id
    where prices.apartment_type='studio' or prices.apartment_type='1 bedroom';"""

    apartment_df = pd.read_sql(query, conn)
    return apartment_df


def calculate_apartment_data_features():
    cols = ["name", "apartment_type", "price", "All Time Low", "Price Versus All Time Low",
            "Change Versus Last Day", "All Time Low?"]
    apartment_df = get_apartment_data()
    apartment_df["All Time Low"] = None
    apartment_df["Price Versus All Time Low"] = apartment_df["price"].copy()
    apartment_df["Change Versus Last Day"] = apartment_df["price"].copy()
    apartment_df["All Time Low?"] = None

    current_date = apartment_df['date'].max()

    newest_apts_indexes = []
    grouped_apartments = apartment_df.groupby(['name', 'apartment_type'])
    for key, grouped_apartment in grouped_apartments:
        grouped_apartment.sort_values(by="date", ascending=False, inplace=True)
        index = grouped_apartment['date'].idxmax()
        newest_apts_indexes.append(index)

        # Lowest of All Time
        min_all_time = grouped_apartment['price'].min()
        apartment_df.at[index, 'All Time Low'] = min_all_time
        apartment_df.at[index, "Price Versus All Time Low"] -= min_all_time

        # All time low?
        if apartment_df.at[index, "price"] == min_all_time:
            apartment_df.at[index, "All Time Low?"] = "All Time Low"
        else:
            apartment_df.at[index, "All Time Low?"] = '-'

        # Change Versus Last Day
        last_day_index = grouped_apartment.index[1]
        apartment_df.at[index, "Change Versus Last Day"] -= apartment_df.at[last_day_index, "price"]
    return apartment_df.loc[newest_apts_indexes, cols].sort_values(by="price", ascending=True)


def send_email(title, message_text, message_html, sender_email, receiver_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(message_text, "html")
    part2 = MIMEText(message_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create a secure SSL context and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.sendgrid.net", PORT, context=context) as server:
        server.login("apikey", API_KEY)
        server.sendmail(sender_email, receiver_email, message.as_string())


def send_apartment_emails():
    df = calculate_apartment_data_features()

    # Find the lowest price
    filter = (df["price"] < 2500) & (df["Change Versus Last Day"] < 0)
    low = df.loc[filter].iloc[0]

    message_html = df.to_html()
    title = f"Apartments: {low['name']} Changed ${low['Change Versus Last Day']} to ${low['price']}"

    current_date = datetime.datetime.fromtimestamp(time.time())
    readable_date = current_date.strftime('%Y-%m-%d')
    for name, email in zip(RECIPIENT_NAMES, RECIPIENT_EMAILS):
        message_text = f"""<b>Hi, {name}!<\b>\n This is the updated Apartment Prices for {readable_date}\n
                        """

        print(f"Sending message from={RECIPIENT_EMAILS[1]} to {email}")
        send_email(title, message_text, message_html, sender_email=RECIPIENT_EMAILS[1], receiver_email=email)
