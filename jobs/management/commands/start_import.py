from django.core.management import BaseCommand
import os
import glob
from django.conf import settings
from jobs.services import try_start_import


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_mask', nargs='+', type=str)

    def handle(self, *args, **options):
        '''
        варианты использования команды:
        python manage.py start_import "*" - обработает все файлы из папки import/import-data, 
                                            при использовании маски кавычки писать обязательно
        python manage.py start_import first_shop.json second_shop.json - точные имена файлов можно без кавычек
        '''
        file_names = options['file_mask']
        list_files = set()
        for name in file_names:
            path = os.path.join(settings.IMPORT_INCOME, name)
            files = glob.glob(path)
            list_files = list_files | set(files)
        list_files = list(list_files)
        # TODO и если в список не попало ни одного файла, или нет параметров, тоже показать ошибку
        if try_start_import(list_files):
            print("Import is started. Wait for results.")
        else:
            print("Something is wrong. Import cancelled.")
