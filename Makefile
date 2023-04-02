CONFIG_CONVERTER="../SpiderManPCTool v1.1.1-51-v1-1-1-1660951619/Config Converter-2428-1-0-1664221419.exe"
INPUT_DIR=configs
OUTPUT_DIR=build

.PHONY: all
all :$(OUTPUT_DIR)/progression.smpcmod $(OUTPUT_DIR)/challenges.smpcmod

# TODO: This should be the steps the runs the mod maker
$(OUTPUT_DIR)/%.json: $(INPUT_DIR)/%.json
	mkdir -p $(dir $@)
	cp $< $@

%/system_progression.config: %/system_progression.json
	# TODO: Build two mods for this
	python3 scripts/mod-maker.py --input $< --mods skills upgrades
	$(CONFIG_CONVERTER) $<

%/system_challengebasescorelist.config: %/system_challengebasescorelist.json
	python3 scripts/mod-maker.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

$(OUTPUT_DIR)/progression.smpcmod: $(OUTPUT_DIR)/system/system_progression.config progression-mod-info.txt
	scripts/zip-maker.py \
		--zip $@ \
		--input-list $(OUTPUT_DIR)/system/system_progression.config progression-mod-info.txt \
		--output-list ModFiles/0_9C9C72A303FCFA30 SMPCMod.info

$(OUTPUT_DIR)/challenges.smpcmod: $(OUTPUT_DIR)/system/system_challengebasescorelist.config challenges-mod-info.txt
	scripts/zip-maker.py \
		--zip $@ \
		--input-list $(OUTPUT_DIR)/system/system_challengebasescorelist.config challenges-mod-info.txt \
		--output-list ModFiles/0_93E67681DD14D1D7 SMPCMod.info

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)

.SECONDARY:
	# Having this target prevents the deletion of intermediate files
