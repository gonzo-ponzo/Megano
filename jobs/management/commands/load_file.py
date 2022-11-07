from django.core.management import BaseCommand
import os
from django.conf import settings
from bs4 import BeautifulSoup

from product.models import Property, Product, ProductCategory, Manufacturer, ProductProperty


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)
        parser.add_argument('--ok', type=bool, default=False, required=False)
        parser.add_argument('--man', type=int, default=1, required=False)
        parser.add_argument('--cat', type=int, default=1, required=False)

    def handle(self, *args, **options):
        '''
        варианты использования команды:
        python manage.py load_file "название_файла" - спарсит файл, находящийся по адресу "/yandex/название_файла",
                                                      выдаст информацию в консоль
        python manage.py load_file "название_файла" --ok True --cat <category_id> --man <manufacturer_id> - спарсит
                                                    и сохранит запись в базу данных, картинки нужно добавить вручную
        '''
        file_name = options["file_name"]
        file_path = os.path.join(settings.BASE_DIR, "yandex", file_name)
        ok = options["ok"]
        man = options["man"]
        cat = options["cat"]
        with open(file_path, "r") as f:
            contents = f.read()
            soup = BeautifulSoup(contents, "html.parser")
            name = soup.h1.string.strip()
            print(name, "\n")
            description = soup.find(string='Описание').findNext('div').text
            print(description, "\n")
            info = soup.find(string='Коротко о товаре')
            if info:
                properties = info.findNext('table')
            else:
                properties = None
            if ok:
                category = ProductCategory.objects.get(id=cat)
                manufacturer = Manufacturer.objects.get(id=man)
                product = Product.objects.create(name=name, description=description,
                                                 category=category, manufacturer=manufacturer)
            if properties:
                for tr in properties.findAll("tr"):
                    td = tr.findAll("td")
                    if td[1].string and len(td[1].string) > 0:
                        if ok:
                            pr, _ = Property.objects.get_or_create(name=td[0].string)
                            ProductProperty.objects.create(product=product, property=pr, value=td[1].string)
                        else:
                            pr = Property.objects.filter(name=td[0].string).first()
                        print(td[0].string, '\t', pr, '\t', td[1].string)
