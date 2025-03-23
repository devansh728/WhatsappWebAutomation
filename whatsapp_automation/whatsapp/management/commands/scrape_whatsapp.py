import time
from django.core.management.base import BaseCommand
from whatsapp.scraper.whatsapp_scraper import WhatsAppScraper

class Command(BaseCommand):
    help = 'Scrape WhatsApp Web for messages and media'

    def add_arguments(self, parser):
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode',
        )
        parser.add_argument(
            '--no-media',
            action='store_true',
            help='Skip downloading media files',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=0,
            help='Run continuously with the specified interval in minutes (0 for single run)',
        )

    def handle(self, *args, **options):
        headless = options.get('headless', False)
        download_media = not options.get('no_media', False)
        interval = options.get('interval', 0)
        
        self.stdout.write(self.style.SUCCESS('Starting WhatsApp Web scraper'))
        
        # Run once or continuously based on interval
        if interval <= 0:
            self._run_scraper(headless, download_media)
        else:
            self.stdout.write(self.style.SUCCESS(f'Running in continuous mode with {interval} minute interval'))
            try:
                while True:
                    self._run_scraper(headless, download_media)
                    self.stdout.write(self.style.SUCCESS(f'Sleeping for {interval} minutes...'))
                    time.sleep(interval * 60)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Scraper stopped by user'))
    
    def _run_scraper(self, headless, download_media):
        scraper = WhatsAppScraper(headless=headless, download_media=download_media)
        
        try:
            success = scraper.process_all_chats()
            if success:
                self.stdout.write(self.style.SUCCESS('Successfully scraped WhatsApp Web'))
            else:
                self.stdout.write(self.style.ERROR('Failed to scrape WhatsApp Web'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error scraping WhatsApp Web: {str(e)}'))
        finally:
            scraper.close() 