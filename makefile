# testing
test:
	python2 tests.py


# clean dirs and cache
clean:
	rm -r dist
	rm -r build
	find -name '*.pyc' -delete


# upload to pypi
pypi:
	python2 setup.py sdist upload


# make arch package
arch:
	mkdir -p dist/netlog
	cp PKGBUILD dist/netlog
	cd dist; tar -czvf netlog.tar.gz netlog
