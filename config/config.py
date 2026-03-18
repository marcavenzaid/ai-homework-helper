import utilities.utilities as utilities
import definitions

config_json = utilities.read_file_json(definitions.CONFIG_PATH)

FILE_DELETER_AGE_IN_DAYS = config_json["FILE_DELETER_AGE_IN_DAYS"]
FILE_DELETER_MAX_FILES = config_json["FILE_DELETER_MAX_FILES"]

LOG_WHEN = config_json["LOG_WHEN"]
LOG_INTERVAL = config_json["LOG_INTERVAL"]
LOG_BACKUP_COUNT = config_json["LOG_BACKUP_COUNT"]
LOG_FORMATTER_FORMAT = config_json["LOG_FORMATTER_FORMAT"]

TUTOR_BRAIN_TO_USE_CONFIG_TAG_NAME = config_json["TUTOR_BRAIN_TO_USE_CONFIG_TAG_NAME"]
