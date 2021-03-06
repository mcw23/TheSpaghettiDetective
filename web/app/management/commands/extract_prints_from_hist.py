#!/usr/bin/env python
import csv
import sys
from django.core.management.base import BaseCommand, CommandError

from app.models import HistoricalPrinter

class Command( BaseCommand ):
    help = 'Extract prints from history table'

    def handle(self, *args, **options):
        prints = []
        for printer_id in set([k['id'] for k in HistoricalPrinter.objects.values('id')]):
            started = None
            print_filename = None
            alerted_at = None
            for hist in HistoricalPrinter.objects.filter(id=printer_id).order_by('history_id'):
                if hist.current_print_filename:
                    if not started or print_filename != hist.current_print_filename:
                        print_filename = hist.current_print_filename
                        started = hist.current_print_started_at
                else:
                    if started:
                        prints += [dict(
                            filename=print_filename,
                            start=started,
                            end=hist.history_date,
                            alert=alerted_at,
                            start_secs=int(started.timestamp()),
                            end_secs=int(hist.history_date.timestamp()),
                            alert_secs=int(alerted_at.timestamp()) if alerted_at else '',
                            id=hist.id)]
                        started = None
                        print_filename = None
                        alerted_at = None
                if hist.current_print_alerted_at and started:
                        alerted_at = hist.current_print_alerted_at

        w = csv.DictWriter(sys.stdout, prints[0].keys())
        w.writeheader()
        w.writerows(prints)
