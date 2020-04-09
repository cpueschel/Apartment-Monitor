import pandas as pd
import sendgrid
import os
from sendgrid.helpers.mail import *

from db_init import conn
from settings import EMAIL_RECIPIENTS


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


def send_emails():
    # TODO: Convert the dataframe over to a html table & email it out once a day!
    df = calculate_apartment_data_features()

    # Find the lowest price
    filter = (df["price"] < 2500) & (df["Change Versus Last Day"] < 0)
    low = df.loc[filter].iloc[0]

    html = df.to_html()
    title = f"Apartments: {low['name']} Changed ${low['Change Versus Last Day']} to ${low['price']}"

    # Now Send the HTML In an email

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("from_email@example.com")
    to_email = To("from_email@example.com")
    subject = "Sending with SendGrid is Fun"
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)



