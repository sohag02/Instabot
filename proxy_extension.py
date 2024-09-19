import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import zipfile
import logging

logger = logging.getLogger(__name__)

# Create the Chrome extension zip file
def create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password, dir):
    logging.info(f"Creating Proxy Extension for {proxy_host}")
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """

    background_js = f"""
    var config = {{
      mode: "fixed_servers",
      rules: {{
        singleProxy: {{
          scheme: "http",
          host: "{proxy_host}",
          port: parseInt({proxy_port})
        }},
        bypassList: ["localhost"]
      }}
    }};

    chrome.proxy.settings.set(
      {{value: config, scope: "regular"}},
      function() {{}}
    );

    chrome.webRequest.onAuthRequired.addListener(
      function(details) {{
        return {{
          authCredentials: {{
            username: "{proxy_username}",
            password: "{proxy_password}"
          }}
        }};
      }},
      {{urls: ["<all_urls>"]}},
      ['blocking']
    );
    """

    # Create a directory for the extension
    extension_dir = f'{dir}/proxy_auth_extension'
    os.makedirs(extension_dir, exist_ok=True)

    # Write manifest.json and background.js
    with open(os.path.join(extension_dir, 'manifest.json'), 'w') as f:
        f.write(manifest_json)
    with open(os.path.join(extension_dir, 'background.js'), 'w') as f:
        f.write(background_js)

    # Zip the extension files
    extension_zip = f'{dir}/proxy_auth_extension.zip'
    with zipfile.ZipFile(extension_zip, 'w') as zp:
        zp.write(os.path.join(extension_dir, 'manifest.json'), 'manifest.json')
        zp.write(os.path.join(extension_dir, 'background.js'), 'background.js')

    logging.info(f"Proxy Extension created successfully at {extension_zip}")
    return extension_zip
