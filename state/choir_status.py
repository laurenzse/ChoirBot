import datetime
import jsonpickle

from utils.group_members import BasicGroupMember

CHOIR_STATUS_FILE = 'choir_status.json'

LAST_WISH = 'last_wish'
ABSENCES = 'absences'
REMINDERS = 'reminders'
ADMINS = 'admins'
REHEARSAL_DURATION = 'rehearsal_duration'
REHEARSAL_DAY = 'rehearsal_day'
REHEARSAL_TIME = 'rehearsal_time'
CHOIR_CHAT_ID = 'choir_chat_id'


try:
    with open(CHOIR_STATUS_FILE) as f:
        json_string = f.read()
    choir_attributes = jsonpickle.decode(json_string)
except FileNotFoundError:
    choir_attributes = {}


def prepare_status(attribute_name, default_value, to_dict):
    if attribute_name not in to_dict:
        to_dict[attribute_name] = default_value


def prepare_attributes():
    prepare_status(LAST_WISH, BasicGroupMember(name=str(chr(0))), choir_attributes)
    prepare_status(ABSENCES, [], choir_attributes)
    prepare_status(REMINDERS, [], choir_attributes)
    prepare_status(ADMINS, [-1], choir_attributes)  # insert user ids here

    prepare_status(REHEARSAL_DURATION, 120, choir_attributes)
    prepare_status(REHEARSAL_DAY, 2, choir_attributes) # default is wednesday, weekday ints start at monday
    prepare_status(REHEARSAL_TIME, (18, 30), choir_attributes)
    # prepare_status('rehearsal_day', 3, loaded_status) # test input
    # prepare_status('rehearsal_time', (22, 30), loaded_status)

    prepare_status(CHOIR_CHAT_ID, -1, choir_attributes)  # insert a chat id here


prepare_attributes()


def reset_to_default():
    global choir_attributes
    choir_attributes = {}
    prepare_attributes()


# we use tuple lists (a list containing tuple pairs of the member and the associated content)
# for saving different member data; this allows us to serialize the data using json
# (json only allows strings as dictionary keys)

def remove_member_from_tuple_list(member, tuple_list):
    delete_index = get_index_in_tuple_list(member, tuple_list)
    if delete_index is not None:
        tuple_list.pop(delete_index)


def get_index_in_tuple_list(member, tuple_list):
    for index, element in enumerate(tuple_list):
        if element[0] == member:
            return index
    return None


def member_in_tuple_list(member, tuple_list):
    maybe_index = get_index_in_tuple_list(member, tuple_list)
    return maybe_index is not None


def add_reminder(user, text):
    # use group member since we may not know full details about the user (now or in the future)
    choir_attributes[REMINDERS].append((BasicGroupMember.from_telegram_user(user), text))


def clear_reminders():
    choir_attributes[REMINDERS] = []


def get_reminders():
    return choir_attributes[REMINDERS]


def get_reminder_of_user(user):
    member = BasicGroupMember.from_telegram_user(user)
    member_index = get_index_in_tuple_list(member, choir_attributes[REMINDERS])
    if member_index is not None:
        return choir_attributes[REMINDERS][member_index][1]
    else:
        return None


def remove_reminder_of_user(user):
    member = BasicGroupMember.from_telegram_user(user)
    remove_member_from_tuple_list(member, choir_attributes[REMINDERS])


def add_absence(user, start_date, end_date):
    absence = {'start': start_date, 'end': end_date}

    # use group member to allow json serialization, also we may not know every detail about the user at any given point
    choir_attributes[ABSENCES].append((BasicGroupMember.from_telegram_user(user), absence))


def get_absence_of_user(user):
    member = BasicGroupMember.from_telegram_user(user)
    member_index = get_index_in_tuple_list(member, choir_attributes[ABSENCES])
    if member_index is not None:
        absence = choir_attributes[ABSENCES][member_index][1]
        return absence['start'], absence['end']
    else:
        return None


def remove_absence_of_user(user):
    member = BasicGroupMember.from_telegram_user(user)
    remove_member_from_tuple_list(member, choir_attributes[ABSENCES])


def clean_up_absences():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    remove = []

    for (absent_member, absence) in choir_attributes[ABSENCES]:
        absence_end = absence['end']

        if absence_end <= yesterday:
            remove.append(absent_member)

    for member in remove:
        remove_absence_of_user(member)


def absences_at_date(date):
    current_absences = []

    for (absent_member, absence) in choir_attributes[ABSENCES]:
        absence_start = absence['start']
        absence_end = absence['end']

        if absence_start <= date < absence_end:
            current_absences.append(absent_member)

    return current_absences


def next_rehearsal_datetime(after_datetime):
    rehearsal_datetime = after_datetime + datetime.timedelta((choir_attributes[REHEARSAL_DAY] - after_datetime.weekday()) % 7)

    hour, minute = choir_attributes[REHEARSAL_TIME]
    rehearsal_datetime = rehearsal_datetime.replace(hour=hour, minute=minute, second=0, microsecond=0)

    while after_datetime > rehearsal_datetime:
        rehearsal_datetime = rehearsal_datetime + datetime.timedelta(weeks=1)

    return rehearsal_datetime


def next_rehearsal_date(after_date):
    after_datetime = datetime.datetime.combine(after_date, datetime.datetime.min.time())
    return next_rehearsal_datetime(after_datetime).date()


def rehearsal_at_datetime(check_datetime, tolerance=0):
    if check_datetime.weekday() != choir_attributes[REHEARSAL_DAY]:
        return False

    hour, minute = choir_attributes[REHEARSAL_TIME]
    rehearsal_start = datetime.datetime(check_datetime.year, check_datetime.month, check_datetime.day,
                                        hour=hour, minute=minute)

    duration = choir_attributes[REHEARSAL_DURATION]

    rehearsal_end = rehearsal_start + datetime.timedelta(minutes=duration)

    # account for tolerance...

    tolerance_duration = duration * tolerance

    rehearsal_start = rehearsal_start - datetime.timedelta(minutes=tolerance_duration)
    rehearsal_end = rehearsal_end + datetime.timedelta(minutes=tolerance_duration)

    return rehearsal_start < check_datetime < rehearsal_end


def is_admin(user):
    return user.id in choir_attributes[ADMINS]


def access_attributes():
    return choir_attributes


def get_choir_attribute(item_name):
    return access_attributes()[item_name]


def set_choir_attribute(item_name, value):
    if item_name == ADMINS and not value:
        return False
    if item_name in choir_attributes:
        choir_attributes[item_name] = value
        return True
    return False


def save_data():
    out_json_string = jsonpickle.encode(choir_attributes)
    with open(CHOIR_STATUS_FILE, 'w') as outfile:
        outfile.write(out_json_string)