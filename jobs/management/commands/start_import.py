from django.core.management import BaseCommand

from jobs.services import try_start_import


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_mask', nargs='+', type=str)

    def handle(self, *args, **options):
        file_names = options['file_mask']  # TODO превратить маску/маски в список файлов
        # и если в список не попало ни одного файла, или нет параметров, тоже показать ошибку
        if try_start_import(file_names):
            print("Import is started. Wait for results.")
        else:
            print("Something is wrong. Import cancelled.")
