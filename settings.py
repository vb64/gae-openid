DEBUG = True
#DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Admin', 'vit.sar68@gmail.com'),
)

MANAGERS = ADMINS

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'gae-openid.middleware.OpenIDMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    'tpl',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
)
