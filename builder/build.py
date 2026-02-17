import zipfile
import os

def create_plugin_zip():
    output_filename = 'image_optimizer.zip'
    files_to_include = [
        '__init__.py',
        'config_dialog.py',
        'main.py',
        'optimizer.py',
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
                arcname = f
                if 'builder/' in f:
                    arcname = os.path.basename(f)
                print(f"Adding {f} as {arcname}...")
                zf.write(f, arcname)
            
            print("Adding images/icon.png...")
            zf.write('images/icon.png')

            # Add translations
            if os.path.exists('translations'):
                for root, dirs, files in os.walk('translations'):
                    for file in files:
                        if file.endswith('.mo'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('translations', file)
                            print(f"Adding {arcname}...")
                            zf.write(file_path, arcname)

            
        print(f"Successfully created {output_filename}")
    except Exception as e:
        print(f"Error creating zip: {e}")

if __name__ == '__main__':
    create_plugin_zip()
