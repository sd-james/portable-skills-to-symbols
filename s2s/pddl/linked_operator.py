from collections import defaultdict

from typing import List, Tuple, Dict

from s2s.pddl.pddl_operator import PDDLOperator
from s2s.pddl.pddl_operator import _PrettyPrint as PP
from s2s.pddl.pddl import Proposition, Clause, Probabilistic, RewardPredicate, ConditionalEffect, FluentPredicate, \
    MixedEffect
from s2s.utils import indent


class LinkedPDDLOperator(PDDLOperator):

    def __init__(self, pddl_operator: PDDLOperator):
        """
        Create a new PDDL operator
        :param learned_operator: the estimated operator
        :param name: the name of the operator (optional)
        :param task: the task ID (ignore this if there is only one task)
        """
        self.pddl_operator = pddl_operator
        self._links = defaultdict(list)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("attempted to get missing private attribute '{}'".format(name))
        return getattr(self.pddl_operator, name)

    @property
    def links(self):
        return self._links

    def add_link(self, start, end, prob):
        self._links[start].append((end, prob))

    def pretty_print(self, index=None, option_descriptor=None, **kwargs):
        """
        Print everything out nicely
        """
        probabilistic = kwargs.get('probabilistic', True)
        use_rewards = kwargs.get('use_rewards', True)
        conditional_effects = kwargs.get('conditional_effects', True)
        return str(_PrettyPrint(self, index, probabilistic, use_rewards, conditional_effects, option_descriptor))


class _PrettyPrint(PP):

    def __init__(self, operator: LinkedPDDLOperator, index=None, probabilistic=True, use_rewards=True,
                 conditional_effects=True, option_descriptor=None):
        super().__init__(operator, index, probabilistic, use_rewards, option_descriptor)
        self._conditional_effects = conditional_effects

    def __str__(self):

        if self._probabilistic:
            effects = self._operator.effects
        else:
            effects = [max(self._operator.effects, key=lambda x: x[0])]  # get most probable

        if self._conditional_effects:
            return self._make_conditional_operator(self._operator.preconditions, effects, self._operator.links)

        return '\n\n'.join(
            self._make_operator(i, self._operator.preconditions, effects, start, link_effects) for
            i, (start, link_effects)
            in enumerate(self._operator.links.items()))

    def _make_operator(self, link_index: int, preconditions: List[Proposition],
                       effects: List[Tuple[float, List[Proposition], float]],
                       start_link: int, link_effects: List[Tuple[int, float]]):

        if self._conditional_effects:
            raise ValueError("Should be using _make_conditional_operator function")

        start_prop = Proposition('psymbol_{}'.format(start_link), None)
        precondition = Clause(preconditions) + start_prop

        for end_link, link_prob in link_effects:

            effect = Probabilistic()
            for prob, eff, reward in effects:
                if self._use_rewards and reward is not None:
                    clause = Clause(eff + [RewardPredicate(reward)])  # add the reward
                else:
                    clause = Clause(eff)
                prob *= link_prob
                if end_link != -1:  # end partition changed!
                    clause += Proposition('psymbol_{}'.format(end_link), None)

                effect.add(clause, prob)

            if len(effects) > 1:
                effect = '\n' + indent(str(effect), 2)
            else:
                effect = str(effect)

            if self._option_descriptor is None:
                name = self._operator.name
            else:
                name = '{}-partition-{}'.format(self._option_descriptor(self._operator.option),
                                                self._operator.partition)
            if self._index is not None:
                name += '-{}'.format(self._index)

            name += '-{}'.format(link_index)  # to avoid duplicate names

            return '(:action {}\n\t:parameters ()\n\t:precondition {}\n\t:effect {}\n)'.format(name,
                                                                                               precondition,
                                                                                               effect)

    def _make_conditional_operator(self, preconditions: List[Proposition],
                                   effects: List[Tuple[float, List[Proposition], float]],
                                   link_effects: Dict[int, List[Tuple[int, float]]]):

        if not self._conditional_effects:
            raise ValueError("Should be using _make_operator function")

        precondition = Clause(preconditions)
        effect = Probabilistic()
        for prob, eff, reward in effects:
            if self._use_rewards and reward is not None:
                clause = Clause(eff + [RewardPredicate(reward)])  # add the reward
            else:
                clause = Clause(eff)
            effect.add(clause, prob)

        conditional_effects = list()

        precondition_links = Clause(conjunctive=False)
        for start, next_links in link_effects.items():
            link_pre = FluentPredicate('=', 'linking', start)
            precondition_links += link_pre
            link_effect = Probabilistic()
            for end, link_prob in next_links:
                if end != -1:
                    link_effect.add(FluentPredicate('assign', 'linking', end), link_prob)
            if len(link_effect) > 0:
                conditional_effects.append(ConditionalEffect(link_pre, link_effect))

        mixed_effect = MixedEffect(effect, conditional_effects)
        if len(mixed_effect) > 1:
            effect = '\n' + indent(str(mixed_effect), 2)
        else:
            effect = str(mixed_effect)

        if self._option_descriptor is None:
            name = self._operator.name
        else:
            name = '{}-partition-{}'.format(self._option_descriptor(self._operator.option),
                                            self._operator.partition)
        if self._index is not None:
            name += '-{}'.format(self._index)

        return '(:action {}\n\t:parameters ()\n\t:precondition {}\n\t:effect {}\n)'.format(name, precondition,
                                                                                                    # precondition_links,
                                                                                                    effect)
