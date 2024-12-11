import os
import re
import sys
import subprocess

# Adjust path relative to the current script location
PLUGIN_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../plugin.py')

def parse_plugin_file():
    plugin_data = {}
    with open(PLUGIN_FILE_PATH, 'r') as plugin_file:
        content = plugin_file.read()
        plugin_data_section = re.search(r'self\.plugindata\s*=\s*{\n(.*?)\n}', content, re.DOTALL)
        if plugin_data_section:
            plugin_lines = plugin_data_section.group(1).split('\n')
            for line in plugin_lines:
                match = re.match(r'\s*"(?P<key>[^"]+)"\s*:\s*\["(?P<author>[^"]+)",\s*"(?P<repository>[^"]+)",\s*"(?P<description>[^"]+)",\s*"(?P<branch>[^"]+)"\],?', line.strip())
                if match:
                    plugin_info = match.groupdict()
                    plugin_data[plugin_info["key"]] = plugin_info
    return plugin_data

def validate_repository(author, repository, branch):
    repo_url = f"https://github.com/{author}/{repository}"
    repo_clone_cmd = f"git ls-remote --heads {repo_url} {branch}"
    result = subprocess.run(repo_clone_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {repo_clone_cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
    return result.returncode == 0

def main():
    print("Parsing plugin file...")
    plugin_data = parse_plugin_file()
    print(f"Parsed data: {plugin_data}")
    
    all_valid = True
    for key, data in plugin_data.items():
        print(f"Validating repository for plugin: {key}")
        is_valid = validate_repository(data["author"], data["repository"], data["branch"])
        if is_valid:
            print(f"✅ Repository {data['author']}/{data['repository']} on branch {data['branch']} is valid.")
        else:
            print(f"❌ Repository {data['author']}/{data['repository']} on branch {data['branch']} is invalid.")
            all_valid = False

    if not all_valid:
        print("One or more plugins are invalid.")
        sys.exit(1)  # Exit with a non-zero code to indicate failure

if __name__ == "__main__":
    main()
