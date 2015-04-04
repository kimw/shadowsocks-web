all:
	@echo 'Usage: make (run | debug | clean | demo)'

run:
	python3 web.py

debug: clean
	python3 web.py -v

demo:
	python3 web.py --demo

clean:
	py3clean .
	pyclean .
