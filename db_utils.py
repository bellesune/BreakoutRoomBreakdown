import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func
from db_instance import DB
import models

AVAILABLE_TIMES = [9, 11, 13, 15]

def add_or_get_auth_user(ucid, name):
    existing_user = (DB.session.query(models.AuthUser)
                        .filter(
                            func.lower(models.AuthUser.ucid) == func.lower(ucid)
                        ).first())
    if existing_user:
        user_info = models.UserInfo(
            id=existing_user.id,
            ucid=existing_user.ucid,
            role=models.UserRole(existing_user.role),
            name=existing_user.name,
        )
    else:
        new_user = models.AuthUser(
            ucid=ucid,
            auth_type=models.AuthUserType.GOOGLE,
            role=models.UserRole.STUDENT,
            name=name,
        )
        DB.session.add(new_user)
        DB.session.flush()
        user_info = models.UserInfo(
            id=new_user.id,
            ucid=new_user.ucid,
            role=models.UserRole(new_user.role),
            name=new_user.name,
        )

    DB.session.commit()
    return user_info

def get_all_room_ids():
    rooms = DB.session.query(models.Room).all()
    room_ids = [room.id for room in rooms]
    DB.session.commit()
    return room_ids

def get_number_of_rooms():
    rooms_count = DB.session.query(func.count(models.Room.id)).scalar()
    DB.session.commit()
    return rooms_count

def get_available_room_ids_for_date(date):
    appointments = (DB.session.query(models.Appointment)
                            .filter(
                                func.DATE(models.Appointment.start_time) == date,
                            ).all())
    room_ids_by_time = {}
    all_room_ids = get_all_room_ids()
    for appointment in appointments:
        room_ids_by_time.setdefault(appointment.date.hour, set(all_room_ids))
        room_ids_by_time[appointment.date.hour].discard(appointment.room_id)
    DB.session.commit()
    return room_ids_by_time

def get_available_times_for_date(date):
    room_availability = get_available_room_ids_for_date(date)
    total_rooms = get_number_of_rooms()
    availability = {
        hour: (total_rooms - len(room_availability.get(hour, [])))
        for hour in AVAILABLE_TIMES
    }
    DB.session.commit()
    return availability

def get_available_dates_after_date(date, date_range=3):
    assert date_range >= 0
    cutoff_date = date + datetime.timedelta(days=date_range)
    unavailable_date_models = (DB.session.query(models.UnavailableDate)
                                .filter(
                                    and_(
                                        func.DATE(models.UnavailableDate.date) >= date.date(),
                                        func.DATE(models.UnavailableDate.date) <= cutoff_date.date(),
                                    ),
                                ).all())
    unavailable_dates = set(model.date.date() for model in unavailable_date_models)
    all_dates_in_range = set(
        date.date() + datetime.timedelta(days=day)
        for day in range(date_range)
    )
    available_dates = set()
    for possible_date in all_dates_in_range:
        available_times = get_available_times_for_date(possible_date)
        free_timeslots = len([
            hour
            for hour, free in available_times.items()
            if free > 0
        ])
        if free_timeslots > 0:
            available_dates.add(possible_date)

    DB.session.commit()
    return list(
        datetime.datetime(available.year, available.month, available.day)
        for available in available_dates.difference(unavailable_dates)
    )

def get_attendee_ids_from_ucids(ucids):
    lower_ucids = [ucid.lower() for ucid in ucids]
    existing_attendee_models = (DB.session.query(models.Attendee)
                            .filter(
                                func.lower(
                                    models.Attendee.ucid
                                ).in_(
                                    lower_ucids
                                )
                            ).all())
    existing_attendees = {
        attendee.id: attendee.ucid
        for attendee in existing_attendee_models
    }
    new_attendees = [
        models.Attendee(ucid) for ucid in lower_ucids
        if ucid not in existing_attendees.values()
    ]
    DB.session.add_all(new_attendees)
    DB.session.flush()
    new_attendee_ids = [attendee.id for attendee in new_attendees]
    DB.session.commit()

    return list(existing_attendees.keys()).extend(new_attendee_ids)
