tests = tests
user = biologyguy
module = PyTattle
#pytestops = "--full-trace"
#pytestops = "-v -s"
repo = $(user)/$(module)
desc = Release $(version)

BUILD = python setup.py install $(installargs)
TEST = py.test $(pytestops) $(tests)

all:
	$(BUILD)
	$(TEST)

install:
	$(BUILD)

test:
	$(TEST)

docs:
	make -C docs api
	make -C docs html

readme:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	pandoc --from=markdown --to=rst --output=CHANGES.rst CHANGES.md

lint:
	pylint $(module)

clean:
	rm -Rf __pycache__
	rm -Rf **/__pycache__/*
	rm -Rf dist
	rm -Rf build
	rm -Rf *.egg-info

github_release:
	curl -v -i -X POST \
		-H "Content-Type:application/json" \
		-H "Authorization: token $(token)" \
		https://api.github.com/repos/$(repo)/releases \
		-d '{"tag_name":"$(version)","target_commitish": "master","name": "$(version)","body": "$(desc)","draft": false,"prerelease": false}'

release:
	$(clean)
	# tag
	git tag $(version)
	# build
	$(BUILD)
	$(TEST)
	python setup.py sdist bdist_wheel
	# release
	twine register dist/$(module)-$(version).tar.gz
	twine upload dist/$(module)-$(version).tar.gz
	git push origin --tags
	$(github_release)
