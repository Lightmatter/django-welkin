import json
from pathlib import Path

from django.core.management.base import BaseCommand

from ...models import CDT


# pylint: disable=no-member
class Command(BaseCommand):
    help = "Imports data from Welkin Designer configuration export"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            "json",
            metavar="configuration_file",
            help="Welkin Designer configuration export JSON",
        )

    def handle(self, *args, **options):
        with Path(options["json"]).open(encoding="utf-8") as f:
            data = json.load(f)

            self.stdout.write("Import CDTs")
            for cdt in data["cdts"]:
                if cdt.pop("internal"):
                    self.stdout.write(f'Skip internal CDT {cdt["name"]}')
                    continue

                cdt["contains_phi"] = cdt.pop("_containsPHI")

                _, created = CDT.objects.update_or_create(**cdt)
                self.stdout.write(
                    f'{"Created" if created else "Updated"} CDT {cdt["name"]}'
                )
