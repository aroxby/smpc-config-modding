CONFIG_CONVERTER="../SpiderManPCTool v1.1.1-51-v1-1-1-1660951619/Config Converter-2428-1-0-1664221419.exe"
INPUT_DIR=configs
OUTPUT_DIR=build

.PHONY: all
all :$(OUTPUT_DIR)/progression.smpcmod $(OUTPUT_DIR)/challenge_scores.smpcmod

# TODO: This should be the steps the runs the mod maker
$(OUTPUT_DIR)/%.json: $(INPUT_DIR)/%.json
	mkdir -p $(dir $@)
	cp $< $@

%/system_progression.config: %/system_progression.json
	# Note: Can't build two mods for this because they would each replace the entire progression system
	python3 scripts/mod-maker.py --input $< --mods skills upgrades
	$(CONFIG_CONVERTER) $<

%/system_challengebasescorelist.config: %/system_challengebasescorelist.json
	python3 scripts/mod-maker.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

%/system_challengectns1scorelist.config: %/system_challengectns1scorelist.json
	python3 scripts/mod-maker.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

%/system_challengectns2scorelist.config: %/system_challengectns2scorelist.json
	python3 scripts/mod-maker.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

%/system_challengectns3scorelist.config: %/system_challengectns3scorelist.json
	python3 scripts/mod-maker.py --input $< --mods challenges
	$(CONFIG_CONVERTER) $<

$(OUTPUT_DIR)/progression.smpcmod: progression-mod-info.txt $(OUTPUT_DIR)/system/system_progression.config
	scripts/zip-maker.py \
		--zip $@ \
		--input-list progression-mod-info.txt $(OUTPUT_DIR)/system/system_progression.config \
		--output-list SMPCMod.info ModFiles/0_9C9C72A303FCFA30

$(OUTPUT_DIR)/challenge_scores.smpcmod: \
 challenges-mod-info.txt \
 $(OUTPUT_DIR)/system/system_challengebasescorelist.config \
 $(OUTPUT_DIR)/system/system_challengectns1scorelist.config \
 $(OUTPUT_DIR)/system/system_challengectns2scorelist.config \
 $(OUTPUT_DIR)/system/system_challengectns3scorelist.config
	scripts/zip-maker.py \
		--zip $@ \
		--input-list \
			challenges-mod-info.txt \
			$(OUTPUT_DIR)/system/system_challengebasescorelist.config \
			$(OUTPUT_DIR)/system/system_challengectns1scorelist.config \
			$(OUTPUT_DIR)/system/system_challengectns2scorelist.config \
			$(OUTPUT_DIR)/system/system_challengectns3scorelist.config \
		--output-list \
			SMPCMod.info \
			ModFiles/0_93E67681DD14D1D7 \
			ModFiles/0_99172CCC995B6D91 \
			ModFiles/0_848E94EC9FF134F3 \
			ModFiles/0_8FF9FCF36268FC2D


.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)

.SECONDARY:
	# Having this target prevents the deletion of intermediate files
