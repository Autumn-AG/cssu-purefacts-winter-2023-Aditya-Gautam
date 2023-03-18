def convert_time(inpt: str) -> int:
    # This  function converts a string representing 24hr format time into number
    # of minutes as an integer for easier calculations.
    a = inpt.split(':')
    return (60 * int(a[0])) + int(a[1])


def undo_convert_time(inpt: int) -> str:
    # This function converts an integer time representation back into a string
    # representation of it in 24hr format.
    hrs = str(inpt // 60)
    mns = str(inpt % 60)
    if len(mns) == 1:
        mns = '0' + mns
    return hrs + ':' + mns


def get_busy_time_list(filename: str) -> list:
    # This function returns a list containing strings for each client from a
    # csv file containing meetings of each client and their times.
    # The strings are of the form "Client#,st1,et1,st2,et2..."
    # where st#,et# are start and end time strings of that client's meetings.
    fl = open(filename, 'r')

    # Take all the data as a large string representation.
    f = fl.read()

    # Remove the field string in the beginning of the csv file.
    fd = f[f.find('\n')+1:]

    # Count the number of new line characters.
    i = fd.count('\n')
    while i > 1:
        # Index over the new line characters.
        ind = fd.find('\n')
        if fd[ind+1] == ',':
            # This is to add a new meeting to the same client.
            fd = fd[:ind] + fd[ind+1:]
        else:
            # This is to split the string for clients.
            fd = fd[:ind] + '_' + fd[ind+1:]
        i -= 1

    # This removes the newline character at the end of the string.
    output = fd[:-1].split('_')
    fl.close()
    return output


def get_free_time_dict(inpt: list) -> dict:
    # This function returns a dictionary from a Client-meetings list.
    # For each string of the form "Client#,st1,et1,st2,et2..."
    # An element is added to the dictionary, where the "Client#" string is the
    # key and the duration they are free for is a list containing nested lists
    # which have start time of the free period, and its duration.
    output = {}
    for client_str in inpt:
        # This splits the Client string into a list.
        new_list = client_str.split(',')

        # As the day starts at 9:00 and ends at 17:00, we can add them to the
        # list and take the negatives of the busy times.
        new_list.insert(1, '9:00')
        new_list.append('17:00')
        lng = len(new_list)
        sub_list = []
        i = 1
        while i < lng:
            # As the client strings are now lists of the form:
            # ["Client#","9:00","st1","et1","st2" ... , "17:00"]
            # We can index over the odd indexes and subtract subsequent times
            # To get the negatives of the busy times, i.e., the free times.
            st = convert_time(new_list[i])
            et = convert_time(new_list[i+1])
            ft = et-st

            if ft > 0:
                # This avoids adding time slots with 0 duration.
                sub_list.append([st, et-st])

            i += 2

        # This creates a nested list of all the free times.
        output[new_list[0]] = sub_list
    return output


def free_time_all_clients(inpt: dict) -> list | None:
    # From a dictionary of free times of all clients, this function creates a
    # nested list containing list of all times when all clients are free.
    # Each sub-list is of the form - [<start time of free period>,< duration>]
    fin_list = []

    # Here we add a base value by taking the first client in the dictionary
    # for comparison.
    base = list(inpt.keys())[0]
    fin_list.extend(inpt[base])

    for client in inpt:
        # We create an accumulator to see if a client's free times are
        # considered in the final times.
        chk_1 = 0

        # Avoiding re-checking for the base client.
        if client == base:
            chk_1 += 1

        else:
            # Loop over all free times in the final list.
            for ftb in fin_list:
                # Create an accumulator to see if a free time in the list has
                # been compared to a client.
                chk_2 = 0
                st = ftb[0]
                et = st + ftb[1]
                for ft in inpt[client]:
                    # This checks for each free time slot of the client.
                    fts = ft[0]
                    fte = fts + ft[1]

                    # Checking for overlap in the final list, and for client.
                    if (fts < et) and (st < fte):
                        # This selects the overlap period of the two time slots
                        # by choosing the latest starting point and earliest.
                        # ending point.
                        ffs = max(fts, st)
                        ffe = min(fte, et)
                        ftb[0] = ffs
                        ftb[1] = ffe - ffs
                        # Adding to the accumulators.
                        chk_1, chk_2 = chk_1 + 1, chk_2 + 1
                if chk_2 == 0:
                    # If a time period in the time list had no times in common
                    # with a client (accumulator == 0), it is removed from the
                    # final list.
                    fin_list.remove(ftb)

        if chk_1 == 0:
            # If a client had no times overlapping in the final list, then there
            # is no free time (accumulator = 0). Hence the output is None.
            return None

    # Outputs the final list.
    return fin_list


def get_max_free_time(schedule_csv_file: str) -> str | None:
    # Get a list of client-meetings from the file.
    busy_time = get_busy_time_list(schedule_csv_file)
    # Convert to a dictionary of free times for the clients.
    free_times = get_free_time_dict(busy_time)
    # Check when all clients are free as a nested list of time slots.
    free_time_for_all_clients = free_time_all_clients(free_times)

    if free_time_for_all_clients is None:
        # Return None when no free time period was there for all clients.
        return None

    else:
        # Set the first time as the base time.
        answer = (free_time_for_all_clients[0][0],
                  free_time_for_all_clients[0][1])

        # Iterate over other times (if any)
        for time in free_time_for_all_clients:
            # Longer duration free slot
            if time[1] > answer[1]:
                answer = tuple(time)
            # Earlier free slot.  **
            if time[1] == answer[1]:
                if time[0] < answer[0]:
                    answer = tuple(time)
        # **: As it was not specified which time period should be chosen in case
        # of a tie, the program chooses the earlier time.

        # This converts the time back into 24hr format.
        start_time = undo_convert_time(answer[0])
        duration = str(answer[1])

        # For a tuple output, comment lines 182, 183, 184 and uncomment line 181
        # return (start_time, duration)
        return "The maximum free time period where all clients are available " \
               "is at " + start_time + " and is for a duration of " + \
            duration + " minutes."

