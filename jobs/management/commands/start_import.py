from django.core.management import BaseCommand
import os
import glob
from django.conf import settings
from jobs.services import try_start_import

from jobs.tasks import shop_import


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_mask', nargs='+', type=str)
        parser.add_argument('--mail', type=str, default=None, required=False)

    def handle(self, *args, **options):
        help = '''
        варианты использования команды:
        python manage.py start_import "*" - обработает все файлы из папки import/import-data,
                                            при использовании маски кавычки писать обязательно
        python manage.py start_import first_shop.json second_shop.json - точные имена файлов можно без кавычек
        python manage.py start_import "*" --mail admin@email.to - с адресом, куда отправить файл с логом
        '''
        file_names = options["file_mask"]
        email_admin = options["mail"]
        list_files = set()
        for name in file_names:
            path = os.path.join(settings.IMPORT_INCOME, name)
            files = set(filter(lambda x: os.path.isfile(x), glob.glob(path)))
            list_files = list_files | files
        list_files = list(list_files)
        if len(list_files) == 0:
            print("Файлов для импорта не найдено, попробуйте указать другие настройки.", help)
            return

        # TODO временно:
        shop_import(list_files, "shop_import", email_admin)

        # такое должно быть:
        #if try_start_import(list_files):
        #    print("Import is started. Wait for results.")
        #else:
        #    print("Something is wrong. Import cancelled.")
