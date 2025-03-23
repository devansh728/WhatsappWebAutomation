import os
import time
import json
import logging
from datetime import datetime
from urllib.parse import urljoin
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from django.conf import settings
from whatsapp.models import ChatMessage, MediaFile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(settings.BASE_DIR, 'whatsapp_scraper.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class WhatsAppScraper:
    def __init__(self, headless=False, download_media=True):
        """
        Initialize the WhatsApp Web scraper
        
        Args:
            headless (bool): Run browser in headless mode
            download_media (bool): Whether to download media files
        """
        self.headless = headless
        self.download_media = download_media
        self.driver = None
        self.chat_list = []
        self.media_dir = os.path.join(settings.MEDIA_ROOT, 'whatsapp')
        
        # Create media directory if it doesn't exist
        if not os.path.exists(self.media_dir):
            os.makedirs(self.media_dir)
    
    def initialize_driver(self):
        """Set up and initialize the Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Add user data directory to maintain session
        user_data_dir = os.path.join(settings.BASE_DIR, 'chrome_data')
        options.add_argument(f'--user-data-dir={user_data_dir}')
        
        self.driver = webdriver.Chrome(options=options)
        
        logger.info("WebDriver initialized successfully")
        return self.driver
    
    def open_whatsapp_web(self):
        """Open WhatsApp Web and wait for scan/login"""
        self.driver.get('https://web.whatsapp.com/')
        
        # Wait for WhatsApp to load - look for the search box
        try:
            logger.info("Waiting for WhatsApp Web to load...")
            search_box = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            logger.info("WhatsApp Web loaded successfully")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for WhatsApp Web to load. Please scan the QR code.")
            return False
    
    def get_chat_list(self):
        """Get list of available chats"""
        try:
            # Wait for chat list to load
            chat_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@aria-label="Chat list"]//div[@role="row"]'))
            )
            
            # Extract chat names and click to open
            self.chat_list = []
            for chat in chat_list:
                try:
                    chat_name = chat.find_element(By.XPATH, './/span[@dir="auto"][@title]').get_attribute('title')
                    self.chat_list.append({'name': chat_name, 'element': chat})
                except NoSuchElementException:
                    continue
            
            logger.info(f"Found {len(self.chat_list)} chats")
            return self.chat_list
        except Exception as e:
            logger.error(f"Error getting chat list: {str(e)}")
            return []
    
    def open_chat(self, chat_item):
        """
        Open a specific chat
        
        Args:
            chat_item: Dict containing chat information
        """
        try:
            chat_item['element'].click()
            # Wait for messages to load
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error opening chat {chat_item['name']}: {str(e)}")
            return False
    
    def extract_messages(self, chat_name):
        """
        Extract all messages from the current open chat
        
        Args:
            chat_name: Name of the chat (sender/receiver)
            
        Returns:
            List of extracted message dictionaries
        """
        try:
            # Wait for messages container to load
            message_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-panel-messages"]'))
            )
            
            # Extract all message bubbles
            message_elements = message_container.find_elements(By.XPATH, './/div[@role="row"]')
            
            messages = []
            for msg_element in message_elements:
                try:
                    # Determine if it's an outgoing or incoming message
                    is_outgoing = 'message-out' in msg_element.get_attribute('class')
                    sender = 'You' if is_outgoing else chat_name
                    receiver = chat_name if is_outgoing else 'You'
                    
                    # Extract timestamp
                    try:
                        timestamp_element = msg_element.find_element(By.XPATH, './/div[@data-testid="msg-meta"]')
                        timestamp_str = timestamp_element.text
                        # Parse the timestamp (expected format like "10:42 AM")
                        timestamp = datetime.now()  # Default to now, but we'll extract the time
                        date = timestamp.date()
                    except:
                        timestamp = datetime.now()
                        date = timestamp.date()
                    
                    # Extract message text
                    try:
                        message_text = msg_element.find_element(By.XPATH, './/div[@data-testid="msg-text"]').text
                    except:
                        message_text = ""
                    
                    # Extract media elements
                    media_urls = []
                    
                    # Check for images
                    try:
                        images = msg_element.find_elements(By.XPATH, './/img[contains(@src, "blob:")]')
                        for img in images:
                            media_urls.append({
                                'type': 'image',
                                'url': img.get_attribute('src')
                            })
                    except:
                        pass
                    
                    # Check for videos
                    try:
                        videos = msg_element.find_elements(By.XPATH, './/video')
                        for video in videos:
                            media_urls.append({
                                'type': 'video',
                                'url': video.get_attribute('src')
                            })
                    except:
                        pass
                    
                    # Get unique message ID
                    msg_id = msg_element.get_attribute('data-id') or f"{time.time()}"
                    
                    # Create message object
                    message = {
                        'sender': sender,
                        'receiver': receiver,
                        'message': message_text,
                        'timestamp': timestamp,
                        'date': date,
                        'chat_id': msg_id,
                        'media_urls': json.dumps(media_urls) if media_urls else None
                    }
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    continue
            
            logger.info(f"Extracted {len(messages)} messages from chat with {chat_name}")
            return messages
        
        except Exception as e:
            logger.error(f"Error extracting messages: {str(e)}")
            return []
    
    def download_media(self, message, media_data):
        """
        Download media files from a message
        
        Args:
            message: The ChatMessage object
            media_data: List of media URL dictionaries
            
        Returns:
            List of MediaFile objects created
        """
        media_files = []
        
        for media_item in media_data:
            try:
                media_type = media_item.get('type', 'unknown')
                media_url = media_item.get('url')
                
                if not media_url:
                    continue
                
                # Generate filename
                file_ext = 'jpg' if media_type == 'image' else 'mp4' if media_type == 'video' else 'bin'
                filename = f"{media_type}_{int(time.time())}_{len(media_files)}.{file_ext}"
                file_path = os.path.join(self.media_dir, filename)
                
                # Download file
                response = requests.get(media_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    
                    # Create MediaFile object
                    media_file = MediaFile(
                        chat_message=message,
                        file_name=filename,
                        file_type=media_type,
                        file_url=media_url,
                        file_path=file_path,
                        downloaded=True
                    )
                    media_file.save()
                    media_files.append(media_file)
                
            except Exception as e:
                logger.error(f"Error downloading media: {str(e)}")
                continue
        
        return media_files
    
    def save_messages_to_db(self, messages, chat_name):
        """
        Save extracted messages to the database
        
        Args:
            messages: List of message dictionaries
            chat_name: Name of the chat
            
        Returns:
            Number of messages saved
        """
        count = 0
        
        for msg_data in messages:
            try:
                # Check if message already exists by chat_id
                if ChatMessage.objects.filter(chat_id=msg_data['chat_id']).exists():
                    continue
                
                # Create new ChatMessage
                message = ChatMessage(
                    sender=msg_data['sender'],
                    receiver=msg_data['receiver'],
                    message=msg_data['message'],
                    timestamp=msg_data['timestamp'],
                    date=msg_data['date'],
                    chat_id=msg_data['chat_id'],
                    media_urls=msg_data['media_urls']
                )
                message.save()
                count += 1
                
                # Download media if available
                if self.download_media and msg_data['media_urls']:
                    media_data = json.loads(msg_data['media_urls'])
                    self.download_media(message, media_data)
                
            except Exception as e:
                logger.error(f"Error saving message to database: {str(e)}")
                continue
        
        logger.info(f"Saved {count} new messages from chat with {chat_name}")
        return count
    
    def process_all_chats(self):
        """Process all available chats"""
        try:
            self.initialize_driver()
            if not self.open_whatsapp_web():
                return False
            
            chats = self.get_chat_list()
            total_messages = 0
            
            for chat in chats:
                try:
                    logger.info(f"Processing chat with {chat['name']}")
                    
                    if self.open_chat(chat):
                        messages = self.extract_messages(chat['name'])
                        saved = self.save_messages_to_db(messages, chat['name'])
                        total_messages += saved
                
                except Exception as e:
                    logger.error(f"Error processing chat {chat['name']}: {str(e)}")
                    continue
            
            logger.info(f"Completed processing {len(chats)} chats, saved {total_messages} new messages")
            return True
            
        except Exception as e:
            logger.error(f"Error in process_all_chats: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed") 