setup:
	@docker build -t dns_provider .
run:
	@docker run -p 80:8000 dns_provider
test:
	@coverage run --source=./ -m unittest discover --start-directory ./tests -p "*.py"
