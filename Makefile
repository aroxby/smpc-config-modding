CONFIG_CONVERTER="../SpiderManPCTool v1.1.1-51-v1-1-1-1660951619/Config Converter-2428-1-0-1664221419.exe"

.PHONY: all
all: progression.smpcmod

%.config: %.json
	python3 recode.py $<
	$(CONFIG_CONVERTER) $<

progression.smpcmod: config/system/system_progression.config SMPCMod.info
	7z a -tzip -mx=9 $@ ./$^
	7z rn $@ system_progression.config ModFiles/0_9C9C72A303FCFA30
