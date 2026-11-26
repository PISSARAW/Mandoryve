.PHONY: demo test

demo:
	@code=0; python3 -m mandoryve examples/group.json || code=$$?; test "$$code" -eq 1

test:
	python3 -m unittest discover -s tests -v

.PHONY: setup quality

setup:
	git config --local core.hooksPath .githooks

quality:
	sh quality/gate.sh staged
