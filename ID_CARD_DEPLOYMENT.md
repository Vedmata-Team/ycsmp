# ID Card Download Deployment Fix

## Problem
The ID card download functionality works locally but fails in deployment because it requires Chrome browser and ChromeDriver for HTML-to-image conversion.

## Solutions

### Solution 1: Install Chrome and ChromeDriver (Recommended)

1. **Run the installation script on your server:**
   ```bash
   chmod +x install_chrome.sh
   sudo ./install_chrome.sh
   ```

2. **Verify installation:**
   ```bash
   google-chrome --version
   chromedriver --version
   ```

3. **Restart your Django application**

### Solution 2: Use wkhtmltopdf (Alternative)

1. **Install wkhtmltopdf on server:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install wkhtmltopdf
   
   # CentOS/RHEL
   sudo yum install wkhtmltopdf
   ```

2. **Update URL configuration to use alternative view:**
   ```python
   # In ID/urls.py, replace:
   path('card/<int:registration_id>/', views.generate_id_card, name='generate_card'),
   # With:
   path('card/<int:registration_id>/', alternative_views.generate_id_card_wkhtmltopdf, name='generate_card'),
   ```

### Solution 3: Docker Deployment

If using Docker, add to your Dockerfile:
```dockerfile
# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1) && \
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver
```

## Testing

1. **Test the download URL directly:**
   ```bash
   curl -I "http://your-domain.com/id/card/3568/?format=PNG"
   ```

2. **Check server logs for errors:**
   ```bash
   tail -f /var/log/nginx/error.log
   tail -f /path/to/django/logs/django.log
   ```

3. **Test Chrome installation:**
   ```bash
   google-chrome --headless --no-sandbox --dump-dom https://www.google.com
   ```

## Common Issues

1. **Permission denied**: Ensure ChromeDriver has execute permissions
2. **Display issues**: Add `--no-sandbox` and `--disable-dev-shm-usage` flags
3. **Memory issues**: Add `--disable-gpu` and `--disable-extensions` flags
4. **Font issues**: Install required fonts on server

## Monitoring

Add logging to track ID card generation:
```python
import logging
logger = logging.getLogger(__name__)

# In your view
logger.info(f"Generating ID card for registration {registration_id}")
```



sudo apt-get install wkhtmltopdf
