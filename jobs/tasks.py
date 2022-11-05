import os
from datetime import datetime
from django.conf import settings

from payment.celery import app
from .models import Process


@app.task(name="shop_import", track_started=True)
def shop_import(file_names, pr_name, email=None):
    from .services import one_shop_import, send_mail_from_site
    name_log = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
    ok, fail, parted = 0, 0, 0
    file_import = os.path.join(settings.IMPORT_LOGS, name_log)
    with open(file_import, "w") as f:
        for file_name in file_names:
            name = os.path.basename(file_name)
            is_ok, messages = one_shop_import(file_name)
            # писать в логи нужное, переносить файл в соответствующую папку
            print(file_name, is_ok, file=f)
            if type(messages) != str:
                messages = "\n".join(messages)
            print(messages, file=f)
            if is_ok:
                ok += 1
                new_path = os.path.join(settings.IMPORT_DONE, name)
            else:
                new_path = os.path.join(settings.IMPORT_FAIL, name)
                if messages.startswith("ERROR"):
                    fail += 1
                else:
                    parted += 1
            os.rename(file_name, new_path)
            print("----------", file=f)
    short_stat = f"{ok} imports done successfully\n{parted} - has warnings\n{fail} - cancelled"
    print(short_stat)
    if email:
        send_mail_from_site("Import done", short_stat, [email], file_import)
    process, _ = Process.objects.get_or_create(name=pr_name)
    process.is_run = False
    process.save()
    return "import done"
