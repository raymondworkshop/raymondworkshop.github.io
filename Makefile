#automate tasks in general
.PHONY: help init run memex serve push

help:
	@echo "myblog Makefile"
	@echo ""
	@echo "  make init              Install Python dependencies"
	@echo "  make run               Build site (_posts -> docs/)"
	@echo "  make memex CMD=stats   Run memex CLI (stats, missing, top, ...)"
	@echo "  make site             Start local preview server"
	@echo "  make push              Commit and push to git"

init:
	python3 -m pip install -r requirements.txt

run:
	python3 blog.py

memex:
	python3 memex.py $(CMD)

site:
	python3 -m server.py

push:
	git add .
	git diff --cached --quiet || git commit -m "update"
	git push
