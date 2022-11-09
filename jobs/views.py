import os
import secrets
import string
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth.decorators import permission_required

from .models import Process
from jobs.services import try_start_import


class ImportForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}), label=_("Файлы для импорта:"))
    email = forms.CharField(required=False, label=_("Электронная почта (для уведомления):"))


def id_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(secrets.choice(chars) for _ in range(size))


def save_uploaded_file(f):
    file_name = f.name
    file_path = os.path.join(settings.IMPORT_INCOME, file_name)
    while os.path.isfile(file_path):  # пока не найдем свободное имя файла
        file_name = f"{id_generator()}_{f.name}"
        file_path = os.path.join(settings.IMPORT_INCOME, file_name)
    with open(file_path, "wb") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


@permission_required('jobs.start_import')
def shop_import(request):
    process, fl = Process.objects.get_or_create(name="shop_import")
    if request.method == "POST":
        import_form = ImportForm(request.POST, request.FILES)
        if import_form.is_valid():
            files = request.FILES.getlist("files")
            names = []
            for f in files:
                names.append(save_uploaded_file(f))
            status, message = try_start_import(names, import_form.cleaned_data["email"])
            return redirect(reverse("shop_import"))
    else:
        import_form = ImportForm()
    context = {"is_run": process.is_run, "import_form": import_form}
    return render(request, "jobs/import.html", context=context)
