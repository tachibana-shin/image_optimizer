import zipfile
import os

def create_plugin_zip():
    output_filename = 'image_optimizer.zip'
    files_to_include = [
        '__init__.py',
        'main.py',
        'optimizer.py',
        'config_dialog.py',
        'plugin-import-name-image_optimizer.txt'
    ]
    
    # Check if files exist
    missing_files = []
    for f in files_to_include:
        if not os.path.exists(f):
            missing_files.append(f)
            
    if not os.path.exists('images/icon.png'):
        missing_files.append('images/icon.png')
        
    if missing_files:
        print(f"Error: Missing files: {missing_files}")
        return

    try:
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files_to_include:
                print(f"Adding {f}...")
                zf.write(f)
            
            print("Adding images/icon.png...")
            zf.write('images/icon.png')
            
        print(f"Successfully created {output_filename}")
    except Exception as e:
        print(f"Error creating zip: {e}")

if __name__ == '__main__':
    create_plugin_zip()
