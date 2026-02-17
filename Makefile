.PHONY: all clean

all: image_optimizer.zip

image_optimizer.zip: build.py __init__.py main.py optimizer.py config_dialog.py plugin-import-name-image_optimizer.txt
	python build.py

load:
	calibre-customize -b .

dev: load
	calibre-debug -g

clean:
	python -c "import os; os.remove('image_optimizer.zip') if os.path.exists('image_optimizer.zip') else None"
