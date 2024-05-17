#TODO:fjern ubrugte varabler

ITEMS_PER_PAGE = 2

USER_PER_PAGE = 6

#TODO:skal denne være længere
# Strengen skal have præcis 32 tegn.
# Strengen kan kun indeholde tegnene fra 'a' til 'f' og '0' til '9'.
USER_ID_LEN = 32
USER_ID_REGEX = "^[a-f0-9]{32}$"


USER_EMAIL_MAX = 100
USER_EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"



# Strengen skal kun indeholde engelske små bogstaver (ingen store bogstaver, tal, specialtegn osv.).
# Strengens længde skal være mellem 2 og 20 tegn.
# Strengen skal starte og slutte med et lille bogstav.
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = "^[a-z]{2,20}$"


# Strengen skal have en længde på mellem 2 og 20 tegn.
# Strengen kan indeholde hvilken som helst karakter (bogstaver, tal, specialtegn osv.) undtagen linjeskift.
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 21
USER_REGEX = "^.{2,20}$"

USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 22


# Strengen skal have en længde på mellem 6 og 50 tegn.
# Strengen kan indeholde hvilken som helst karakter (bogstaver, tal, specialtegn osv.) undtagen linjeskift.
USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 50
USER_PASSWORD_REGEX = "^.{6,50}$"


ITEM_NAME_REGEX = "^[a-zA-Z0-9\s]{1,100}$"
ITEM_IMAGE_REGEX = "^[a-zA-Z0-9_\-]+\.(jpg|jpeg|png|gif|webp)$"
ITEM_LATLON_REGEX = "^-?\d{1,3}\.\d+$"
ITEM_STARS_REGEX = "^[1-5]$"
ITEM_PRICE_REGEX = "^\d+(\.\d{1,2})?$"

ITEM_NAME_MIN = 1
ITEM_NAME_MAX = 100