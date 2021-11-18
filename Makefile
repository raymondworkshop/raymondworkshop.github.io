#automate tasks in general
init:
	python3 -m pip install -r requirements.txt

push:
	git add .
	git commit -m "update" .
	git push && git push --tags

run:
	python3 blog.py
