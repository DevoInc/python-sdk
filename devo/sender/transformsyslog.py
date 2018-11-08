"""
Module with the class for Syslog message transform
"""

# More info in RFC 3164: https://tools.ietf.org/html/rfc3164
FACILITY_KERN = 0  # kernel messages
FACILITY_USER = 1  # user-level messages
FACILITY_MAIL = 2  # mail system
FACILITY_DAEMON = 3  # system daemons
FACILITY_AUTH = 4  # security/authorization messages
FACILITY_SYSLOG = 5  # messages generated internally by syslog
FACILITY_LPR = 6  # line printer subsystem
FACILITY_NEWS = 7  # network news subsystem
FACILITY_UUCP = 8  # UUCP subsystem
FACILITY_CLOCK = 9  # clock daemon
FACILITY_AUTHPRIV = 10  # security/authorization messages
FACILITY_FTP = 11  # FTP daemon
FACILITY_NTP = 12  # NTP subsystem
FACILITY_LOG_AUDIT = 13  # log audit
FACILITY_LOG_ALERT = 14  # log alert
FACILITY_CRON = 15  # scheduling daemon
FACILITY_LOCAL0 = 16  # local use 0 (local0)
FACILITY_LOCAL1 = 17  # local use 1 (local1)
FACILITY_LOCAL2 = 18  # local use 2 (local2)
FACILITY_LOCAL3 = 19  # local use 3 (local3)
FACILITY_LOCAL4 = 20  # local use 4 (local4)
FACILITY_LOCAL5 = 21  # local use 5 (local5)
FACILITY_LOCAL6 = 22  # local use 6 (local6)
FACILITY_LOCAL7 = 23  # local use 7 (local7)
# More info in RFC 5424: https://tools.ietf.org/html/rfc5424
SEVERITY_EMERG = 0  # System is unusable
SEVERITY_ALERT = 1  # Should be corrected immediately
SEVERITY_CRIT = 2  # Critical conditions
SEVERITY_ERROR = 3  # Error conditions
SEVERITY_WARN = 4  # May indicate that an error will occur if action is
# not taken.
SEVERITY_NOTICE = 5  # Events that are unusual, but not error conditions.
SEVERITY_INFO = 6  # Normal operational messages that require no action.
SEVERITY_DEBUG = 7  # Information useful to developers for debugging
# the application.
COMPOSE = '%s%s'
COMPOSE_BYTES = b'%s%s'
FORMAT_MY = '<%d>%s %s %s: '  # Not \000
FORMAT_MY_BYTES = b'<%d>%s %s %s: '  # Not \000

# logging.handler translator to Sender codes
facility_names = {
    "auth": FACILITY_AUTH,
    "authpriv": FACILITY_AUTHPRIV,
    "cron": FACILITY_CRON,
    "daemon": FACILITY_DAEMON,
    "ftp": FACILITY_FTP,
    "kern": FACILITY_KERN,
    "lpr": FACILITY_LPR,
    "mail": FACILITY_MAIL,
    "news": FACILITY_NEWS,
    "security": FACILITY_AUTH,  # DEPRECATED
    "syslog": FACILITY_SYSLOG,
    "user": FACILITY_USER,
    "uucp": FACILITY_UUCP,
    "local0": FACILITY_LOCAL0,
    "local1": FACILITY_LOCAL1,
    "local2": FACILITY_LOCAL2,
    "local3": FACILITY_LOCAL3,
    "local4": FACILITY_LOCAL4,
    "local5": FACILITY_LOCAL5,
    "local6": FACILITY_LOCAL6,
    "local7": FACILITY_LOCAL7,
}

priority_map = {
    "EMERG": SEVERITY_EMERG,
    "ALERT": SEVERITY_ALERT,
    "CRITICAL": SEVERITY_CRIT,
    "CRIT": SEVERITY_CRIT,
    "ERROR": SEVERITY_ERROR,
    "ERR": SEVERITY_ERROR,
    "WARNING": SEVERITY_WARN,
    "WARN": SEVERITY_WARN,  # DEPRECATED
    "NOTICE": SEVERITY_NOTICE,
    "INFO": SEVERITY_INFO,
    "DEBUG": SEVERITY_DEBUG
}