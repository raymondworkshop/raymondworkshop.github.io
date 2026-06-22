#automate tasks in general
init:
	python3 -m pip install -r requirements.txt

run:
	python3 blog.py  

serve:
	python3 -m server.py    

push:
	git add .
	git diff --cached --quiet || git commit -m "update"
	git push


