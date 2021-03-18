import time
import math
import subprocess
import SQLiteDriver
import gbl


class User:
    def __init__(self, eamil, mac_address, is_home=0, not_found=10):
        self.email = eamil
        self.mac_address = mac_address
        self.is_home = is_home
        self.not_found = not_found

    def __str__(self):
        return self.email + ", " + self.mac_address + " is home?:" + \
               self.is_home.__str__() + " not found: " + self.not_found.__str__()


def people_home(start,stop):
    users = []
    n_users_home = 0

    # net_ip = '10.105.10.0/24'  # temporarily hard-coded

    with open('knownMAC', 'r') as f:
        for line in f:
            data = line.split(' ')
            users.append(User(data[0], data[1].strip("\n")))  # populate users

    # with open('netconfig.cfg', 'r') as conf:
    #        net_ip = conf.readline()
    net_info = subprocess.check_output(['./findNetwork.sh', 'wlp4s0'])  # get local network info
    net_info = "".join(chr(x) for x in bytearray(net_info))
    [net_ip, net_mask] = net_info.split(' ')
    net_mask_fields = net_mask.split('.')
    nbits = 0
    for field in net_mask_fields:
        nbits += math.log(int(field) + 1, 2)
    net_ip = net_ip + '/' + int(nbits).__str__()

    off = False

    arp_args = net_ip + ' -qg'
    while 1:
        time.sleep(1)
        if n_users_home > 0:
            off = False

        if n_users_home == 0:  # stop the kit from listening
            if not off:
                off = True
                stop()

        nodes = subprocess.check_output(['arp-scan', arp_args])#.splitlines()
        nodes = "".join(chr(x) for x in bytearray(nodes))
        nodes = nodes.splitlines()
        for i in range(2, len(nodes)-3):  # from list of 'ip mac' to list of 'mac'
            nodes[i] = nodes[i].split('\t')[1]
            #print(nodes[i])

        #print("\n")
        for user in users:
            if user.mac_address in nodes:
                if user.is_home == 0:
                    user.is_home = 1  # user just came back home
                    n_users_home += 1
                    welcome(user,start)

                user.not_found = 0  # reset "missing" counter

            else:
                user.not_found += 1
                if user.not_found > 10:  # been away for > 10 scans
                    user.is_home = 0

            #print(user)


def welcome(user,start):
    conn = SQLiteDriver.create_connection("./gHome.sqlite")
    data = SQLiteDriver.get_events(conn, user.email)

    name = SQLiteDriver.get_user_from_email(conn, user.email)

    num = len(data)-1

    altro = "%s" % name

    if num > 0:
        altro = ", Hai %d promemoria salvati" % num

    text = "Bentornato %s." % altro
    gbl.q_speak.put(text)
    start()
    gbl.username = name

people_home(None,None)

