
best_match = []
best_score = -1

def add_calendar(email, weekday, topic):
    return


def get_calendar(email, weekday):
    return


def generate_calendar(users, topics, constraint, include_weekend):  # constrain is nullable, is used if someone
    # can't get the topic done a certain day
    # include_weekend is a boolean
    # #constraint format: [user, day_nope]

    program = []  # association user-day

    #n_user = len(users)
    #n_topics = len(topics)

    n_user = 3
    n_topics = 3

    if include_weekend == 0:
        n_days = 5
    else:
        n_days = 7

    current_match = [0]*n_topics

    global best_match
    best_match = [0]*n_topics
    global best_score
    best_score = -1

    used = [[False]*n_user]*n_days

    comb(current_match, 0, n_user, n_topics, n_days, constraint, used)

    print(best_score)
    print(best_match)


def check_constraints(current_match, constraints):
    for i in range(len(current_match)):
        for j in range(len(constraints)):
            if (constraints[j][0] == current_match[i][0]) and (constraints[j][1] == current_match[i][1]):
                return 0

            if current_match[i][0] is None or current_match[i][1] is None:
                return 0

    return 1


def eval_match(current_match):
    global best_score
    global best_match
    days = []
    users = []
    for match in current_match:
        days.append(match[0])
        users.append(match[1])

    score = len(set(days))+len(set(users))

    if score > best_score:
        best_score = score
        best_match = current_match


def comb(current_match, index, n_user, n_topic, n_days, constraints, used):
    if index >= n_topic:
        print(current_match)
        if check_constraints(current_match, constraints) == 1:
            eval_match(current_match)
            return
    else:
        for i in range(n_days):
            for j in range(n_user):
                current_match[index] = [0]*2

                if not used[i][j]:
                    current_match[index][0] = j
                    current_match[index][1] = i
                else:
                    continue

                if check_constraints(current_match, constraints) != 1:
                    continue

                used[i][j] = True

                comb(current_match, index+1, n_user, n_topic, n_days, constraints, used)

                used[i][j] = False

generate_calendar([], [], [], 0)