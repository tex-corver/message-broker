config_path = $(project_dir)/.configs
project_dir = $(shell pwd)
service = $(shell basename $(project_dir))


.PHONY: unit-test
unit-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/unit --junitxml=unit-test.xml

.PHONY: e2e-test
e2e-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/e2e --junitxml=e2e-test.xml

.PHONY: test
test: 
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests --junitxml=test-report.xml

.PHONY: local-test
local-test:
	CONFIG_PATH=$(config_path) pytest -x $(project_dir)/$(path)