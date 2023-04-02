CONFIG_CONVERTER="../SpiderManPCTool v1.1.1-51-v1-1-1-1660951619/Config Converter-2428-1-0-1664221419.exe"
INPUT_DIR=configs
OUTPUT_DIR=build

.PHONY: all
all :$(OUTPUT_DIR)/progression.smpcmod $(OUTPUT_DIR)/challenges.smpcmod

$(OUTPUT_DIR)/%.json: $(INPUT_DIR)/%.json
	mkdir -p $(dir $@)
	cp $< $@

%/system_progression.config: %/system_progression.json
	python3 recode.py --input $< --mods skills upgrades
	$(CONFIG_CONVERTER) $<

%/system_challengebasescorelist.config: %/system_challengebasescorelist.json
	python3 recode.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

$(OUTPUT_DIR)/progression.smpcmod: $(OUTPUT_DIR)/system/system_progression.config SMPCMod.info
	7z a -tzip -mx=9 $@ ./$^
	7z rn $@ system_progression.config ModFiles/0_9C9C72A303FCFA30

# FIXME: The SMPCMod.info file is the same one from the progression mode
$(OUTPUT_DIR)/challenges.smpcmod: $(OUTPUT_DIR)/system/system_challengebasescorelist.config SMPCMod.info
	7z a -tzip -mx=9 $@ ./$^
	7z rn $@ system_challengebasescorelist.config ModFiles/0_93E67681DD14D1D7

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)

.SECONDARY:
	# Having this target prevents the deletion of intermediate files
