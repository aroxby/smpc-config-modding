#!/usr/bin/env python3
from collections import defaultdict
import json
import sys


class Skill:
    def __init__(self, node):
        self.node = node

    @property
    def name(self):
        return get_by_json_path(self.node, 'Value.Name.Value')

    @property
    def cost(self):
        return int(get_by_json_path(self.node, 'Value.SkillCost.Value'))


class Token:
    def __init__(self, node):
        self.node = node

    @property
    def type(self):  # TODO: Rename this to something that's not a reserve word
        return get_by_json_path(self.node, 'Value')


class Upgrade:
    def __init__(self, node):
        self.node = node

    @property
    def name(self):
        return get_by_json_path(self.node, 'Name.Value')

    @property
    def token_cost(self):
        rsc_path = 'ResourcesPerLevel?.Value.ResourcesNeeded?.Value'
        rsc_nodes = get_by_json_path(self.node, rsc_path)
        rsc_nodes = rsc_nodes or []  # TODO: Figure out how the JSON is expressing `None` for this
        tokens = {}
        for rsc_node in rsc_nodes:
            token = Token(get_by_json_path(rsc_node, 'Value.Item'))
            count = get_by_json_path(rsc_node, 'Value.Count.Value')
            token_type = token.type
            # DEBUG TODO: assert token type not already in dict
            # Temp Debug
            assert token_type not in tokens
            # Temp Debug
            tokens[token_type] = count
        return tokens
        
    @property
    def level_requirement(self):
        return get_by_json_path(self.node, 'Level?.Value')


def recode(path):
    with open(path) as file:
        data = load(file)
    
    # get_upgrades(data)
    # get_skills(data)
    
    # dump(data, sys.stdout)
    with open(path, "w") as file:
        dump(data, file)


def load(file):
    return json.load(file)


def dump(data, file):
    json.dump(data, file, indent=2)



def get_by_json_path(data, path):
    keys = path.split('.')
    debug = []

    for key in keys:
        is_optional = key.endswith('?')
        key = key.rstrip('?')
        if key.isdigit():
            key = int(key)
        try:
            data = data[key]
        except (IndexError, KeyError, TypeError):
            if is_optional:
                return {}
            if isinstance(data, list):
                length = len(data)
                raise KeyError(f'Key {key} wasn\'t in {debug} which has len({length})')
            elif isinstance(data, dict):
                keys = data.keys()
                length = len(keys)
                raise KeyError(f'Key {key} wasn\'t in {debug} which has keys {length} ({keys})')
        debug.append(key)

    return data


def get_upgrades(data):
    list_tree_path = 'Main.TechWebLists.Value'
    list_tree = get_by_json_path(data, list_tree_path)

    item_tree = []
    for list_node in list_tree:
        item_path = 'Value.TechWebItems?.Value'
        item_nodes = get_by_json_path(list_node, item_path)
        if item_nodes:
            item_tree.append(item_nodes)

    # item tree is suits, suit powers, suit mods, *gadgets?

    data_nodes = []
    for item_nodes in item_tree:
        for item_node in item_nodes:
            data_path = 'Value'
            data_node = get_by_json_path(item_node, data_path)
            data_nodes.append(data_node)

    for node in data_nodes:
        upgrade = Upgrade(node)
        print(upgrade.name, ': ', upgrade.level_requirement, upgrade.token_cost)


def get_skills(data):
    upgrade_chains_path = 'Main.Categories.Value.UpgradeChains.Value'
    upgrade_chains = get_by_json_path(data, upgrade_chains_path)

    upgrade_nodes = []
    for upgrade_chain in upgrade_chains:
        upgrades_path = 'Value.Updgrades.Value'
        upgrades = get_by_json_path(upgrade_chain, upgrades_path)
        upgrade_nodes += upgrades

    skills_by_cost = defaultdict(list)
    for node in upgrade_nodes:
        skill = Skill(node)
        cost = skill.cost
        tier = skills_by_cost[cost].append(skill.name)

    print(skills_by_cost)


def main(argv):
    if len(argv) != 2:
        name = argv[0]
        print(f'Usage: {name} [JSON_FILE]', file=sys.stderr)
    path = argv[1]
    recode(path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
