.PHONY: all clean

all: translate image_optimizer.zip

translate:
	pybabel compile -i translations/en.po -o translations/en.mo
	pybabel compile -i translations/vi.po -o translations/vi.mo
	pybabel compile -i translations/ja.po -o translations/ja.mo

image_optimizer.zip: clean
	python builder/build.py

load:
	clear && calibre-customize -b .

dev: load
	calibre-debug -g

clean:
	python -c "import os; os.remove('image_optimizer.zip') if os.path.exists('image_optimizer.zip') else None"
