import re
from figcli.config.constants import VERSION

with open('CHANGELOG.md', 'r') as file:
    changelog = file.read()

regex = f'.*(##+\s+{VERSION}[^#]*)##+\s+[0-9]+\.[0-9]+\.[0-9]+.*'
result = re.search(regex, changelog, re.DOTALL)

if result:
    print(result.group(1).rstrip())
else:
    print(f"Unable to parse changes for new version: {VERSION}")
