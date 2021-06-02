setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

shell:
	./bin/cmd shell

dev:
	./bin/dev

prod:
	./bin/prod
