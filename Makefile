.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf *.egg-info .tox
