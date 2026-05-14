import time
from django.core.management.base import BaseCommand
from railways.models import Train, TrainRunningDay
from railways.scraper import get_running_days_from_web

class Command(BaseCommand):
    help = 'Scrape running days for trains that do not have them in the DB.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Force re-scrape all trains even if they already have running days in DB.',
        )

    def handle(self, *args, **options):
        if options['all']:
            trains_to_scrape = Train.objects.all()
        else:
            # Get trains that have NO running days mapped to them
            trains_to_scrape = Train.objects.filter(running_days__isnull=True).distinct()

        total = trains_to_scrape.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('All trains already have running days. Use --all to force re-scrape.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {total} trains to scrape.'))

        count = 0
        success_count = 0
        fail_count = 0

        for train in trains_to_scrape:
            count += 1
            self.stdout.write(f"[{count}/{total}] Scraping {train.train_no} - {train.train_name[:20]}...")
            
            days = get_running_days_from_web(train.train_no)
            
            if days:
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Success: runs on {', '.join(days)}"))
            else:
                fail_count += 1
                self.stdout.write(self.style.WARNING(f"  Failed: Could not get days for {train.train_no}"))
                
            # Polite delay to avoid IP ban
            time.sleep(1)
            
        self.stdout.write(self.style.SUCCESS(f'Done. Successfully scraped: {success_count}, Failed: {fail_count}'))
