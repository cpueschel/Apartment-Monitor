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


def send_email(title, message_html, sender_email, receiver_email, css=None):
    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    if css is None:
        css = """
        <style>
            table {
              max-width: 100%;
              background-color: transparent;
              border-collapse: collapse;
              border-spacing: 0;
            }
            
            .table {
              width: 100%;
              margin-bottom: 20px;
            }
            
            .table th,
            .table td {
              padding: 8px;
              line-height: 20px;
              text-align: left;
              vertical-align: top;
              border-top: 1px solid #dddddd;
            }
            
            .table th {
              font-weight: bold;
            }
            
            .table thead th {
              vertical-align: bottom;
            }
            
            .table caption + thead tr:first-child th,
            .table caption + thead tr:first-child td,
            .table colgroup + thead tr:first-child th,
            .table colgroup + thead tr:first-child td,
            .table thead:first-child tr:first-child th,
            .table thead:first-child tr:first-child td {
              border-top: 0;
            }
            
            .table tbody + tbody {
              border-top: 2px solid #dddddd;
            }
            
            .table .table {
              background-color: #ffffff;
            }
            
            .table-condensed th,
            .table-condensed td {
              padding: 4px 5px;
            }
            
            .table-bordered {
              border: 1px solid #dddddd;
              border-collapse: separate;
              *border-collapse: collapse;
              border-left: 0;
              -webkit-border-radius: 4px;
                 -moz-border-radius: 4px;
                      border-radius: 4px;
            }
            
            .table-bordered th,
            .table-bordered td {
              border-left: 1px solid #dddddd;
            }
            
            .table-bordered caption + thead tr:first-child th,
            .table-bordered caption + tbody tr:first-child th,
            .table-bordered caption + tbody tr:first-child td,
            .table-bordered colgroup + thead tr:first-child th,
            .table-bordered colgroup + tbody tr:first-child th,
            .table-bordered colgroup + tbody tr:first-child td,
            .table-bordered thead:first-child tr:first-child th,
            .table-bordered tbody:first-child tr:first-child th,
            .table-bordered tbody:first-child tr:first-child td {
              border-top: 0;
            }
            
            .table-bordered thead:first-child tr:first-child > th:first-child,
            .table-bordered tbody:first-child tr:first-child > td:first-child,
            .table-bordered tbody:first-child tr:first-child > th:first-child {
              -webkit-border-top-left-radius: 4px;
                      border-top-left-radius: 4px;
              -moz-border-radius-topleft: 4px;
            }
            
            .table-bordered thead:first-child tr:first-child > th:last-child,
            .table-bordered tbody:first-child tr:first-child > td:last-child,
            .table-bordered tbody:first-child tr:first-child > th:last-child {
              -webkit-border-top-right-radius: 4px;
                      border-top-right-radius: 4px;
              -moz-border-radius-topright: 4px;
            }
            
            .table-bordered thead:last-child tr:last-child > th:first-child,
            .table-bordered tbody:last-child tr:last-child > td:first-child,
            .table-bordered tbody:last-child tr:last-child > th:first-child,
            .table-bordered tfoot:last-child tr:last-child > td:first-child,
            .table-bordered tfoot:last-child tr:last-child > th:first-child {
              -webkit-border-bottom-left-radius: 4px;
                      border-bottom-left-radius: 4px;
              -moz-border-radius-bottomleft: 4px;
            }
            
            .table-bordered thead:last-child tr:last-child > th:last-child,
            .table-bordered tbody:last-child tr:last-child > td:last-child,
            .table-bordered tbody:last-child tr:last-child > th:last-child,
            .table-bordered tfoot:last-child tr:last-child > td:last-child,
            .table-bordered tfoot:last-child tr:last-child > th:last-child {
              -webkit-border-bottom-right-radius: 4px;
                      border-bottom-right-radius: 4px;
              -moz-border-radius-bottomright: 4px;
            }
            
            .table-bordered tfoot + tbody:last-child tr:last-child td:first-child {
              -webkit-border-bottom-left-radius: 0;
                      border-bottom-left-radius: 0;
              -moz-border-radius-bottomleft: 0;
            }
            
            .table-bordered tfoot + tbody:last-child tr:last-child td:last-child {
              -webkit-border-bottom-right-radius: 0;
                      border-bottom-right-radius: 0;
              -moz-border-radius-bottomright: 0;
            }
            
            .table-bordered caption + thead tr:first-child th:first-child,
            .table-bordered caption + tbody tr:first-child td:first-child,
            .table-bordered colgroup + thead tr:first-child th:first-child,
            .table-bordered colgroup + tbody tr:first-child td:first-child {
              -webkit-border-top-left-radius: 4px;
                      border-top-left-radius: 4px;
              -moz-border-radius-topleft: 4px;
            }
            
            .table-bordered caption + thead tr:first-child th:last-child,
            .table-bordered caption + tbody tr:first-child td:last-child,
            .table-bordered colgroup + thead tr:first-child th:last-child,
            .table-bordered colgroup + tbody tr:first-child td:last-child {
              -webkit-border-top-right-radius: 4px;
                      border-top-right-radius: 4px;
              -moz-border-radius-topright: 4px;
            }
            
            .table-striped tbody > tr:nth-child(odd) > td,
            .table-striped tbody > tr:nth-child(odd) > th {
              background-color: #f9f9f9;
            }
            
            .table-hover tbody tr:hover > td,
            .table-hover tbody tr:hover > th {
              background-color: #f5f5f5;
            }
            
            table td[class*="span"],
            table th[class*="span"],
            .row-fluid table td[class*="span"],
            .row-fluid table th[class*="span"] {
              display: table-cell;
              float: none;
              margin-left: 0;
            }
            
            .table td.span1,
            .table th.span1 {
              float: none;
              width: 44px;
              margin-left: 0;
            }
            
            .table td.span2,
            .table th.span2 {
              float: none;
              width: 124px;
              margin-left: 0;
            }
            
            .table td.span3,
            .table th.span3 {
              float: none;
              width: 204px;
              margin-left: 0;
            }
            
            .table td.span4,
            .table th.span4 {
              float: none;
              width: 284px;
              margin-left: 0;
            }
            
            .table td.span5,
            .table th.span5 {
              float: none;
              width: 364px;
              margin-left: 0;
            }
            
            .table td.span6,
            .table th.span6 {
              float: none;
              width: 444px;
              margin-left: 0;
            }
            
            .table td.span7,
            .table th.span7 {
              float: none;
              width: 524px;
              margin-left: 0;
            }
            
            .table td.span8,
            .table th.span8 {
              float: none;
              width: 604px;
              margin-left: 0;
            }
            
            .table td.span9,
            .table th.span9 {
              float: none;
              width: 684px;
              margin-left: 0;
            }
            
            .table td.span10,
            .table th.span10 {
              float: none;
              width: 764px;
              margin-left: 0;
            }
            
            .table td.span11,
            .table th.span11 {
              float: none;
              width: 844px;
              margin-left: 0;
            }
            
            .table td.span12,
            .table th.span12 {
              float: none;
              width: 924px;
              margin-left: 0;
            }
            
            .table tbody tr.success > td {
              background-color: #dff0d8;
            }
            
            .table tbody tr.error > td {
              background-color: #f2dede;
            }
            
            .table tbody tr.warning > td {
              background-color: #fcf8e3;
            }
            
            .table tbody tr.info > td {
              background-color: #d9edf7;
            }
            
            .table-hover tbody tr.success:hover > td {
              background-color: #d0e9c6;
            }
            
            .table-hover tbody tr.error:hover > td {
              background-color: #ebcccc;
            }
            
            .table-hover tbody tr.warning:hover > td {
              background-color: #faf2cc;
            }
            
            .table-hover tbody tr.info:hover > td {
              background-color: #c4e3f3;
            }
            
            h1,
            h2,
            h3,
            h4,
            h5,
            h6 {
              margin: 10px 0;
              font-family: inherit;
              font-weight: bold;
              line-height: 20px;
              color: inherit;
              text-rendering: optimizelegibility;
            }
            
            h1 small,
            h2 small,
            h3 small,
            h4 small,
            h5 small,
            h6 small {
              font-weight: normal;
              line-height: 1;
              color: #999999;
            }
            
            h1,
            h2,
            h3 {
              line-height: 40px;
            }
            
            h1 {
              font-size: 38.5px;
            }
            
            h2 {
              font-size: 31.5px;
            }
            
            h3 {
              font-size: 24.5px;
            }
            
            h4 {
              font-size: 17.5px;
            }
            
            h5 {
              font-size: 14px;
            }
            
            h6 {
              font-size: 11.9px;
            }
            
            h1 small {
              font-size: 24.5px;
            }
            
            h2 small {
              font-size: 17.5px;
            }
            
            h3 small {
              font-size: 14px;
            }
            
            h4 small {
              font-size: 14px;
            }
        </style>
        """
    part1 = MIMEText(css+message_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)

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
        message_text = f"""<h2><b>Hi, {name}!</b></h2>\n <h6>This is the updated Apartment Prices for {readable_date}</h6>\n
                        """

        print(f"Sending message from={RECIPIENT_EMAILS[1]} to {email}")
        send_email(title, message_text + message_html, sender_email=RECIPIENT_EMAILS[1], receiver_email=email)
