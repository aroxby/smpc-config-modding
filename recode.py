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

    @cost.setter
    def cost(self, value):
        cost_node = get_by_json_path(self.node, 'Value.SkillCost')
        cost_node['Value'] = value


class Token:
    def __init__(self, node):
        self.node = node

    @property
    def type_name(self):
        config = get_by_json_path(self.node, 'Value')
        type_name = config\
            .removeprefix('configs/pickup/loot_')\
            .removesuffix('.config')\
            .removesuffix('_01')
        return type_name

    @staticmethod
    def summarize(token_cost):
        REWARD_TYPES = (
            # The order they appear in the UI
            # Research, Landmark, Base, Crime, Challenge, Backpack
            'bio', 'traversal', 'armor',  'battery', 'fiberoptics', 'microchips'
        )
        STORY_TYPES = (
            'impact_web_unlock', 'electric_unlock', 'web_bomb_unlock', 'trip_mine_unlock'
        )
        cost = [0] * len(REWARD_TYPES)
        for token_type, count in token_cost.items():
            if token_type in STORY_TYPES:  # Skip these at least for now
                continue
            if token_type not in REWARD_TYPES:
                raise IndexError(f'Unknown token type: {token_type}')
            index = REWARD_TYPES.index(token_type)
            if cost[index] != 0:
                raise ValueError(f'Repeated token type {token_type}, {cost[index]} -> {count}')
            cost[index] = count
        return cost


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
        rsc_nodes = rsc_nodes or []

        # This can be a single value instead of an array
        if isinstance(rsc_nodes, dict):
            rsc_nodes = [{
                # TODO: It'd be nice to unpack all the other nodes
                # instead of repacking this one to be unpacked later
                'Value': rsc_nodes,
            }]

        tokens = {}
        for rsc_node in rsc_nodes:
            token = Token(get_by_json_path(rsc_node, 'Value.Item'))
            count = get_by_json_path(rsc_node, 'Value.Count.Value')
            token_type = token.type_name
            tokens[token_type] = count
        return tokens

    @property
    def level_requirement(self):
        return get_by_json_path(self.node, 'Level?.Value')

    def remove_token_cost(self):
        # TODO: It would be nice to keep the story tokens
        self.node.pop('ResourcesPerLevel', None)


def recode(path):
    with open(path) as file:
        data = load(file)

    update_skills(data)
    update_upgrades(data)

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

    upgrades = [Upgrade(data_node) for data_node in data_nodes]
    return upgrades


def update_upgrades(data):
    upgrades = get_upgrades(data)
    for upgrade in upgrades:
        upgrade.remove_token_cost()


def get_skills(data):
    upgrade_chains_path = 'Main.Categories.Value.UpgradeChains.Value'
    upgrade_chains = get_by_json_path(data, upgrade_chains_path)

    upgrade_nodes = []
    for upgrade_chain in upgrade_chains:
        upgrades_path = 'Value.Updgrades.Value'
        upgrades = get_by_json_path(upgrade_chain, upgrades_path)
        upgrade_nodes += upgrades

    skills = [Skill(node) for node in upgrade_nodes]
    return skills


def update_skills(data):
    skills = get_skills(data)
    for skill in skills:
        skill.cost = 0


def main(argv):
    if len(argv) != 2:
        name = argv[0]
        print(f'Usage: {name} [JSON_FILE]', file=sys.stderr)
    path = argv[1]
    recode(path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
