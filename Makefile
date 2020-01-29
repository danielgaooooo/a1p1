build:
	docker build -t a1-gtest:0.1 .
	docker run -ti -v `pwd`:/test a1-gtest:0.1 bash -c "cd /test ; make build_exec"

build_exec:
	cp sorer.py sorer
	chmod u+x sorer

test:
	docker build -t a1-gtest:0.1 .
	docker run -ti -v `pwd`:/test a1-gtest:0.1 bash -c "cd /test ; make run_tests"

run_tests:
	python sorer_tests.py

clean:
	rm sorer