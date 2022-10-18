from django.shortcuts import render

from .models import Process


def shop_import(request):
    process, _ = Process.objects.get_or_create(name="shop_import")
    context = {"is_run": process.is_run}  # TODO +form
    return render(request, "jobs/import.html", context=context)
