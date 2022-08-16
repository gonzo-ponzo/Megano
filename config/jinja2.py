from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation

from jinja2 import Environment


def environment(**options):
    env = Environment(extensions=["jinja2.ext.i18n"], **options)

    # Подробнее о подключении расширений
    # https://jinja.palletsprojects.com/en/3.0.x/extensions/
    env.install_gettext_translations(translation)

    # Добавляем все публичные объекты из встроенного
    # пространства имен
    for name, obj in __builtins__.items():
        if not name.startswith("_"):
            env.globals[name] = obj

    # Добавляем ф-ции django
    env.globals.update({
        'static': static,
        'url': reverse,
    })
    return env
