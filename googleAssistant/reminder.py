import SQLiteDriver


def add_reminder(sender, target, timestamp, priority, data):
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    type = "reminder"
    SQLiteDriver.add_event(conn, type, sender, target, timestamp, priority, data)


def get_reminders(target):
    conn = SQLiteDriver.create_connection("gHome.sqlite")
    email = SQLiteDriver.get_email_from_user(conn, target)

    return SQLiteDriver.get_reminders(conn, email)


