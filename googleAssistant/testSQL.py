import SQLiteDriver
import math
import time

conn = SQLiteDriver.create_connection("gHome.sqlite")


#SQLiteDriver.add_user(conn, "Lorenzo", "denisilorenzo@gmail.com", "unmacbello2", "unachiavebella2")
#SQLiteDriver.add_event(conn, "pinco.pallo@gmail.com", "denisilorenzo@gmail.com", "calendario", math.floor(time.time()), 0)
#SQLiteDriver.update_logs(conn, "pinco.pallo@gmail.com")
#print(SQLiteDriver.get_events(conn, "denisilorenzo@gmail.com")[1])
#SQLiteDriver.add_list_item(conn, "noci", 5, 1, "denisilorenzo@gmail.com")
#print(SQLiteDriver.get_list(conn)[1])
#SQLiteDriver.delete_list(conn)
#print(SQLiteDriver.get_user_from_email(conn, "armakim97@gmail.com"))
#SQLiteDriver.remove_last_item(conn)
data = SQLiteDriver.get_reminders(conn, "armakim97@gmail.com")
print(data)