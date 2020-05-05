SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

github:
	@make clean
	@make html
	@bash -c '[ -z "$(ls -l | grep '\.sqlite3')" ] && rm *.sqlite3'
	@bash -c '[ -z "$(ls -l .. | grep '\.js')" ] && rm -rf ../*.js ../*.html ../_*'
	@cp -a _build/html/. ../
	@rm ../objects.inv ../.buildinfo
