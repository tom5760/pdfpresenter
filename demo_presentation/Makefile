DOCS = demo

.PHONY: all clean distclean

all: $(addsuffix .pdf, $(DOCS))

clean:
	-@for file in $(DOCS); do \
		rm $${file}.{aux,log,nav,out,snm,toc} &> /dev/null; \
	done

distclean: clean
	-@for file in $(DOCS); do \
		rm $${file}.pdf &> /dev/null; \
	done

%.pdf: %.tex
	pdflatex -interaction=batchmode -file-line-error $*
	pdflatex -interaction=batchmode -file-line-error $*
	pdflatex -interaction=batchmode -file-line-error $*
