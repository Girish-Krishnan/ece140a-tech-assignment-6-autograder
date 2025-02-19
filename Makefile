build:
	docker build -t assignment-3-autograder --build-arg LOCAL_TEST=true  .

run:
	docker run -it --rm assignment-3-autograder bash
