CONFIG_CONVERTER="../SpiderManPCTool v1.1.1-51-v1-1-1-1660951619/Config Converter-2428-1-0-1664221419.exe"

.PHONY: all
all: config/system/system_progression.config

%.config: %.json
	python3 recode.py $<
	$(CONFIG_CONVERTER) $<