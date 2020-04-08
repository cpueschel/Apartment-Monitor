from db_init import conn

def insert_values(table_name: str, values_string: str):
    c = conn.cursor()
    query = f"""INSERT INTO {table_name} VALUES({values_string})"""
    c.execute(query)
    conn.commit()

def get_id_where(table_name: str, values: dict, id_column=None):
    if id_column is None:
        id_column = 'rowid'
    c = conn.cursor()
    where_items = ' and '.join([f"{key}='{values[key]}'" for key in values.keys()])
    query = f"""SELECT {id_column} FROM {table_name} WHERE {where_items}"""
    c.execute(query)
    rowid = c.fetchone()
    if rowid is not None:
        rowid = rowid[0]
    return rowid
