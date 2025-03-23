import os
import sys
import time
import logging
import django
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatsapp_automation.settings")
django.setup()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_scraper():
    """Run the WhatsApp scraper command"""
    import subprocess
    
    logger.info("Starting WhatsApp scraper job")
    
    try:
        # Execute the Django management command
        subprocess.run(
            ["python", "manage.py", "scrape_whatsapp", "--headless"],
            check=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        logger.info("WhatsApp scraper job completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running WhatsApp scraper: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

def main():
    """Main function to set up and start the scheduler"""
    logger.info("Starting scheduler")
    
    scheduler = BackgroundScheduler()
    
    # Schedule job to run every hour
    scheduler.add_job(
        run_scraper,
        trigger=CronTrigger(hour='*/1'),  # Every hour
        id='whatsapp_scraper',
        name='WhatsApp Web Scraper Job',
        replace_existing=True,
    )
    
    # Add more schedules as needed
    # Example: Run at specific times daily
    # scheduler.add_job(
    #     run_scraper,
    #     trigger=CronTrigger(hour=8, minute=30),  # Every day at 8:30 AM
    #     id='morning_scraper',
    #     name='Morning WhatsApp Scraper',
    #     replace_existing=True,
    # )
    
    try:
        logger.info("Scheduler started, press Ctrl+C to exit")
        scheduler.start()
        
        # Run once immediately
        run_scraper()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {str(e)}")
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shut down")

if __name__ == "__main__":
    main() 