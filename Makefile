DOCKERIM = sitegen

build:
	docker run --rm -v $(shell pwd):/site $(DOCKERIM) build

serve:
	docker run -itv $(shell pwd):/site -p 4000:4000 $(DOCKERIM) serve --host 0.0.0.0

build_image:
	docker build . -t $(DOCKERIM)

.PHONY: build build_image
