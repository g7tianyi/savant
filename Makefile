.PHONY: test stats-words stats-echo help

help:
	@echo "Savant Plugin"
	@echo "  make test          Run state manager tests"
	@echo "  make stats-words   Show Russian words progress"
	@echo "  make stats-echo    Show Russian echo progress"

test:
	python3 scripts/test_state_manager.py

stats-words:
	python3 scripts/state_manager.py stats russian words

stats-echo:
	python3 scripts/state_manager.py stats russian echo
