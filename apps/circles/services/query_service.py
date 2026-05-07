from apps.circles.models import Circle, Cycle


def get_circles():
    return Circle.objects.select_related("teacher")


def get_active_circles():
    return get_circles().filter(is_active=True)


def get_cycles():
    return Cycle.objects.select_related("circle", "circle__teacher")

