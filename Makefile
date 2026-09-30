#automate tasks in general
.PHONY: help init run run-memex memex-build memex memex-enrich serve push

help:
	@echo "myblog Makefile"
	@echo ""
	@echo "  make init              Install Python dependencies"
	@echo "  make run               Fast incremental build with wiki, backlinks, search"
	@echo "  make run-memex         Full rebuild: all HTML + wiki + backlinks + search"
	@echo "  make memex-build       Wiki only: refresh memex pages and indexes (skip other HTML)"
	@echo "  make memex CMD=stats   Run memex CLI (stats, missing, top, ...)"
	@echo "  make memex-enrich      Densify [[wikilinks]] + related: (dry-run; ARGS='--write')"
	@echo "  make site              Start local preview server"
	@echo "  make push              Commit and push to git"

init:
	python3 -m pip install -r requirements.txt

run:
	python3 blog.py --fast

run-memex:
	python3 blog.py --memex

memex-build:
	python3 blog.py --memex-only

memex:
	python3 memex.py $(CMD)

# Densify graph: wrap title mentions + add related: (DRY-RUN default)
#   make memex-enrich ARGS='--write --skip-noisy'
#   make memex-enrich ARGS='--write --section learning'
memex-enrich:
	python3 scripts/memex_enrich.py $(ARGS)

push:
	git add .
	git commit -m "update"
	git push
