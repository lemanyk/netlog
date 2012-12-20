all:
	python2 setup.py sdist
	mkdir -p dist/netlog
	cp PKGBUILD dist/netlog
	cd dist; tar -czvf netlog.tar.gz netlog

clean:
	rm -r dist
	find -name '*.pyc' -delete
