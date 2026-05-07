from django.db import models


class GenderChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class GovernorateChoices(models.TextChoices):
    CAPITAL = "capital", "Capital"
    HAWALLI = "hawalli", "Hawalli"
    FARWANIYA = "farwaniya", "Farwaniya"
    MUBARAK_AL_KABEER = "mubarak_al_kabeer", "Mubarak Al-Kabeer"
    AHMADI = "ahmadi", "Ahmadi"
    JAHRA = "jahra", "Jahra"

