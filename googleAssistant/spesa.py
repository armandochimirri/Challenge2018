import SQLiteDriver


def add_product(name, qt, price, user):
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    email = SQLiteDriver.get_email_from_user(conn, user)

    SQLiteDriver.add_list_item(conn, name, price, qt, email)


def remove_last_item():
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    SQLiteDriver.remove_last_item(conn)


def remove_list():
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    SQLiteDriver.delete_list(conn)


def get_list():
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    return SQLiteDriver.get_list(conn)


def evaluate_credit():
    users = []
    conn = SQLiteDriver.create_connection("gHome.sqlite")

    data = SQLiteDriver.get_users(conn)

    indexes = data[0]

    for i in range(1, len(data)):
        users.append([])
        users[i - 1].append(data[i][indexes["id"]])
        users[i - 1].append(data[i][indexes["email"]])
        users[i - 1].append(data[i][indexes["name"]])
        users[i - 1].append(0)

    sum = 0
    data = SQLiteDriver.get_list(conn)
    indexes = data[0]
    for i in range(1, len(data)):  # for every element in list
        price = data[i][indexes["price"]]
        qt = data[i][indexes["qt"]]
        for j in range(len(users)):  # look for user that purchased
            if users[j][0] == data[i][indexes["user"]]:
                users[j][3] += price * qt  # increment
                sum += (price * qt)  # update sum

    each = sum / len(users)

    for i in range(len(users)):
        users[i][3] -= each  # getting credit subtracting average cost
        users[i][3] = round(users[i][3], 2)  # rounding

    return users

