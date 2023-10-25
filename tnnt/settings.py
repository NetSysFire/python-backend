"""
Django settings for tnnt project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from datetime import datetime, timezone

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
XLOG_DIR = os.path.join(BASE_DIR, 'xlog')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ['tnnt.org']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'scoreboard.apps.ScoreboardConfig',
    'tnnt',
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Required when using Django version 4.x
CSRF_TRUSTED_ORIGINS = []
# CSRF_TRUSTED_ORIGINS = ['https://tnnt.org']

ROOT_URLCONF = 'tnnt.urls'

SETTINGS_PATH = os.path.dirname(__file__)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(SETTINGS_PATH, 'templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tnnt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scoreboard',
        'USER': 'tnnt',
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [ # why is this needed?
        'tnnt/static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session expiration.

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60 # in seconds, so 1 week

# Where you get taken after logging in/out

LOGIN_REDIRECT_URL = '/clanmgmt'
LOGOUT_REDIRECT_URL = '/'

# Custom authentication backend (hooks into dgamelaunch)

AUTHENTICATION_BACKENDS = [
    'tnnt.hardfought_utils.HdfAuthBackend',
]

# Path to dgl sqlite3 database

DGL_DATABASE_PATH = './dgamelaunch_test.db'
# DGL_DATABASE_PATH = '/opt/nethack/chroot/dgldir/dgamelaunch.db'

# Path to where TNNT is writing temp achievement files
# If you don't want to show temp achievements, leave this uncommented
# TEMP_ACHIEVEMENTS_PATH = '/opt/nethack/chroot/tnnt/temp_achievements'

# Clan size limit

MAX_CLAN_PLAYERS = 12

# Clan freeze (no new clan creation / joining clans)

CLAN_FREEZE_TIME = datetime.fromisoformat('2022-11-10T00:00:00+00:00')

# Tournament start/end times

TOURNAMENT_START = datetime.fromisoformat('2022-11-01T00:00:00+00:00')
TOURNAMENT_END   = datetime.fromisoformat('2022-12-01T00:00:00+00:00')

# Main log file

TNNT_LOG_FILE = "tnnt.log"

# Django logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '%(levelname)s %(asctime)s %(message)s',
            'style': '%', # use {} to enclose variables in logging calls
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.FileHandler',
            'filename': TNNT_LOG_FILE,
            'formatter': 'normal',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'normal'
        },
    },
    'root': {
        'handlers': [ 'file', 'console' ],
        'level': 'DEBUG',
    },
}

# URLs of swapchest donor files, which will get downloaded and parsed during
# aggregation.
DONOR_FILES = [
    'https://www.hardfought.org/xlogfiles/tnnt/donors',
    'https://eu.hardfought.org/xlogfiles/tnnt/donors',
    'https://au.hardfought.org/xlogfiles/tnnt/donors'
]

# Regexes for unique deaths handling.
# Rejections are a flat list of regexes that, should they match a death, will
# remove it from consideration.
# Normalizations are a list of 2-tuples of regex and string, which will be the
# first and second arguments to a re.sub() call whose third argument is the
# death string. They are executed in the order they appear here.
UNIQUE_DEATH_REJECTIONS = [
    r"^ascended",
    r"^quit",
    r"^escaped",
]
UNIQUE_DEATH_NORMALIZATIONS = [
    (r"^killed by an ", "killed by a "),
    (r", while .*", ""),
    (r"hallucinogen-distorted ", ""),
    (r"by the invisible ", "by "),
    (r"by (an|a) invisible ", "by a "),
    (r"by invisible ", "by "),
    (r"by .*; the shopkeeper", "by a shopkeeper"),
    (r" (her|his) ", " their "),
    (r" (herself|himself) ", " themselves "),
    (r" (herself|himself)$", " themselves"),
    (r" (called|named) .*", ""),
    # (r" \(with the Amulet\)$", ""), # leave this as a consolation prize
    (r"choked on .*", "choked on something"),
    (r"killed by kicking .*", "killed by kicking something"),
    (r"killed by touching .*", "killed by touching an artifact"),
    # (r"killed by a falling (?!rock)$", "killed by a falling object"), # don't think we need this
    (r" (an? )?M[rs]\. [A-Z].*[,;] the shopkeeper", " a shopkeeper"),
    (r" (an?|the) ghost of .+", " a ghost"),
    (r"poisoned by a rotted .* corpse", "poisoned by a rotted corpse"),
    (r"wrath of .+", "wrath of a deity"),
    (r"priest(ess)?", "priest(ess)"),
    # This next one must come after the last one, because it assumes the
    # priest/priestess has already turned into already priest(ess) with the
    # parens
    (r"priest\(ess\) of .+", "priest(ess) of a deity"),
    # this is ugly... it's the list of things that can be summoned as a minion
    # (to prevent farming a bunch of unique deaths off repeated prayers until
    # the god summons a minion)
    (r"an? (\w+ elemental|Aleax|couatl|Angel|\w+ demon|\w+ devil|(suc|in)cubus|balrog|pit fiend|nalfeshnee|hezrou|vrock|marilith|erinyes) of .+", "minion of a deity"),
]
