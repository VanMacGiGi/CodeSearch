.PHONY: test clean lint

test:
	@echo "Running unit tests..."
	python3 -m unittest discover -s tests -p "test_*.py" -v


clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	
lint:
	flake8 .
