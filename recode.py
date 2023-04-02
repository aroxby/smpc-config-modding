#!/usr/bin/env python3
import argparse
from collections import defaultdict
import json
from os.path import basename
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


class Challenge:
    def __init__(self, node):
        self.node = node

    @property
    def name(self):
        return get_by_json_path(self.node, 'ChallengeName.Value')

    # Note: It'd be really slick to access these tiers like an array but probably not worth it
    @property
    def score_tier_1(self):
        return get_by_json_path(self.node, 'ScoreTier1.Value')

    @property
    def score_tier_2(self):
        return get_by_json_path(self.node, 'ScoreTier2.Value')

    @property
    def score_tier_3(self):
        return get_by_json_path(self.node, 'ScoreTier3.Value')

    @score_tier_1.setter
    def score_tier_1(self, value):
        self.node['ScoreTier1']['Value'] = value

    @score_tier_2.setter
    def score_tier_2(self, value):
        self.node['ScoreTier2']['Value'] = value

    @score_tier_3.setter
    def score_tier_3(self, value):
        self.node['ScoreTier3']['Value'] = value

    @property
    def par_time(self):
        return get_by_json_path(self.node, 'ParTime.Value')

    @par_time.setter
    def par_time(self, value):
        self.node['ParTime']['Value'] = value


def recode(path, mods):
    with open(path) as file:
        data = load(file)

    for mod in mods:
        mod(data)

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

def get_challenges(data):
    challenges_path = 'Main.ChallengeScoreData.Value'
    challenge_nodes = get_by_json_path(data, challenges_path)

    challenges = []
    challenge_path = 'Value'
    for node in challenge_nodes:
        challenges.append(Challenge(get_by_json_path(node, challenge_path)))

    return challenges


def update_challenges(data):
    challenges = get_challenges(data)
    for challenge in challenges:
        challenge.score_tier_1 = 1
        challenge.score_tier_2 = 2
        challenge.score_tier_3 = 3
        # This is not just the max value, it's an even 4.25 minutes
        challenge.par_time = 255


def parse_args(argv, mods):
    parser = argparse.ArgumentParser(basename(argv[0]))
    parser.add_argument('--input', help='path to JSON config', required=True)
    # nargs='+' is supposed to imply required=True
    parser.add_argument('--mods', help='mods to apply', choices=mods, nargs='+', required=True)
    args = parser.parse_args(argv[1:])
    return args


def main(argv):
    available_mods = {
        'skills': update_skills,
        'upgrades': update_upgrades,
        'challenges': update_challenges,
    }

    args = parse_args(argv, available_mods)
    selected_mods = set(available_mods[mod_name] for mod_name in args.mods)
    path = args.input

    recode(path, selected_mods)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
