time_with_col = '\033[96m%(asctime)s\033[0m '

LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
        'access_log': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'access'
        },
        'blure': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': []
        },
    },
    'filters': {},
    'formatters': {
        'default': {
            'format': time_with_col + '%(levelname)-7s %(name)-12s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z',
        },
        'access': {
            'format': time_with_col + 'ACCESS [%(host)s] \033[94m%(status)d\033[0m <- %(request)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z',
        },
    },
    'loggers': {
        'sanic.access': {
            'level': 'DEBUG',
            'handlers': ['access_log'],
            'propagate': False
        },
        'sanic.error': {
            'level': 'DEBUG',
            'handlers': ['default'],
            'propagate': True
        },
        'sanic.root': {
            'level': 'DEBUG',
            'handlers': ['default'],
            'propagate': True
        },
        'blure': {
            'level': 'DEBUG',
            'handlers': ['blure'],
            'propagate': True
        }
    }
}
