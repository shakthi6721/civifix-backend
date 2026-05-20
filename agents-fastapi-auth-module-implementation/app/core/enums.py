from enum import Enum

class Roles(str, Enum):

    SUPER_ADMIN = "SUPER_ADMIN"

    ADMIN = "ADMIN"

    DISTRICT_ADMIN = "DISTRICT_ADMIN"

    INSPECTOR = "INSPECTOR"

    WORKER = "WORKER"

    CITIZEN = "CITIZEN"