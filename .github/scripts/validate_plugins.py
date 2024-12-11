import os
import requests
from plugin import BasePlugin

def validate_repositories():
    plugin_data = BasePlugin().plugindata
    for plugin_key, plugin_info in plugin_data.items():
        author, repository, _, _ = plugin_info
        url = f"https://github.com/{author}/{repository}"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Repository {repository} exists.")
        else:
            print(f"Repository {repository} does not exist.")

if __name__ == "__main__":
    validate_repositories()
