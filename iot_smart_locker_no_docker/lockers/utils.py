from iot_smart_locker_no_docker.lockers.models import Locker


def get_unoccupied_locker():
    available_lockers = Locker.objects.filter(occupied=False)
    return available_lockers.first()


def toggle_locker_status(locker: Locker):
    locker.occupied = not locker.occupied
    locker.save()
    pass
