#automate tasks in general
.PHONY: help init run run-memex memex-build memex serve push

help:
	@echo "myblog Makefile"
	@echo ""
	@echo "  make init              Install Python dependencies"
	@echo "  make run               Fast build: HTML only, no wiki/backlinks"
	@echo "  make run-memex         Full build: HTML + wiki links + backlinks + search"
	@echo "  make memex-build       Wiki only: refresh memex pages and indexes (skip other HTML)"
	@echo "  make memex CMD=stats   Run memex CLI (stats, missing, top, ...)"
	@echo "  make site              Start local preview server"
	@echo "  make push              Commit and push to git"

init:
	python3 -m pip install -r requirements.txt

run:
	python3 blog.py

run-memex:
	python3 blog.py --memex

memex-build:
	python3 blog.py --memex-only

memex:
	python3 memex.py $(CMD)

push:
	git add .
	git diff --cached --quiet || git commit -m "update"
	git push
