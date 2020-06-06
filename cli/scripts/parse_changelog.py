import re
from figgy.config.constants import VERSION

with open('CHANGELOG.md', 'r') as file:
    changelog = file.read()

print(f"Searching for version: {VERSION}")

regex = f'.*(##+\s+{VERSION}.*)##+\s+[0-9]+\.[0-9]+\.[0-9]+.*'
result = re.search(regex, changelog, re.DOTALL)

if result:
    print(result.group(1).rstrip())
else:
    print(f"Unable to parse changes for new version: {VERSION}")
