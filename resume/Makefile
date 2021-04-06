document.pdf: document.html styles.css
	weasyprint document.html document.pdf

document.html: document.pug
	./node_modules/.bin/pug document.pug

styles.css: $(wildcard styles/*.sass)
	./node_modules/.bin/sass styles/styles.sass:styles.css

%PHONY: watch clean

watch: document.pdf
	while true; do \
		inotifywait -e close_write document.pug styles/*.sass;\
		make;\
	done

clean:
	rm -f document.html document.pdf styles.css styles.css.map
