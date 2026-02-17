import re
import datetime
import os

def extract_messages(files):
    messages = []
    # Regex to find _("...") or _('...')
    # Handles escaped quotes arguably well enough for simple cases
    pattern = re.compile(r'_\(["\'](.*?)["\']\)')
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for i, line in enumerate(content.splitlines()):
                matches = pattern.findall(line)
                for msg in matches:
                    messages.append((msg, filepath, i + 1))
    return messages

def create_pot_file(messages, output_file='messages.pot'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')
    header = f"""# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: Image Optimizer 1.0.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {timestamp}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""
    
    unique_msgs = {}
    for msg, file, line in messages:
        if msg not in unique_msgs:
            unique_msgs[msg] = []
        unique_msgs[msg].append((file, line))
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header)
        for msg, locations in unique_msgs.items():
            for loc in locations:
                f.write(f"#: {loc[0]}:{loc[1]}\n")
            f.write(f'msgid "{msg}"\n')
            f.write('msgstr ""\n\n')
            
    print(f"Created {output_file} with {len(unique_msgs)} messages.")

if __name__ == "__main__":
    files = []
    exclude_dirs = {'__pycache__', 'builder', '.git', '.qodo', '.idea', '.vscode'}
    for root, dirs, filenames in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(os.path.join(root, filename))

    if not files:
        print("No python files found.")
    else:
        print(f"Scanning {len(files)} files...")
        msgs = extract_messages(files)
        create_pot_file(msgs, 'translations/messages.pot')
