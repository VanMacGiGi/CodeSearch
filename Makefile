.PHONY: test clean lint install

test:
	@echo "Running unit tests..."
	python3 -m unittest discover -s tests -p "test_*.py" -v


clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	
lint:
	flake8 --max-line-length=88 .

install:
	@echo "Installing..."
	@chmod +x main.py
	@mkdir -p $(HOME)/.local/bin
	@ln -sf $(PWD)/main.py $(HOME)/.local/bin/s
	@echo "Installed 's' command to $(HOME)/.local/bin/s"
