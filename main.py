import configparser
from custom_partitions_script import get_partitions_of_list
from typing import Dict, Union
from dataclasses import dataclass

from math import inf

from os.path import isfile


@dataclass
class Binder:
    assignments: list[str]
    weight: float


@dataclass
class BinderCombination:
    average_carried_weight: float
    assignments_combination: list[list[str]]


def main():
    binder_organizer = BinderOrganizer("configuration.cfg")

    best_3_binder_combination = binder_organizer.get_best_combination_for_n_binders(3)
    print(
        f"With 3 binders, the BEST combination of assignments is {best_3_binder_combination.assignments_combination} with an average carried weight of {best_3_binder_combination.average_carried_weight} Kg\n"
    )

    worse_2_binder_combination = binder_organizer.get_best_combination_for_n_binders(
        2, give_worse_combination=True
    )
    worse_2_binder_combination = worse_2_binder_combination
    print(
        f"With 2 binders, the WORSE combination of assignments is {worse_2_binder_combination.assignments_combination} with an average carried weight of {worse_2_binder_combination.average_carried_weight} Kg\n"
    )

    absolute_best_combination = binder_organizer.get_absolute_best_combination()
    print(
        f"The ABSOLUTE BEST combination with the given options uses {len(absolute_best_combination.assignments_combination)} binders.\nIt is {absolute_best_combination.assignments_combination} with an average carried weight of {absolute_best_combination.average_carried_weight} Kg\n"
    )


class BinderOrganizer:
    def __init__(self, config_file_path):
        self.config = self.try_read_config_file(config_file_path)

        self.weight_per_height_unit = self.read_weight_per_height_unit()
        self.empty_binder_weight = self.read_empty_binder_weight()

        self.weight_per_assignment = self.read_paper_weight_per_assignment()
        self.binder_assignments = self.read_binder_assignments()
        self.schedule = self.read_schedule()

    def try_read_config_file(self, config_file_path: str) -> configparser.ConfigParser:
        if isfile(config_file_path) == False:
            raise ValueError(f"Cannot find configuration file at {config_file_path}")

        config = configparser.ConfigParser()
        config.read(config_file_path)

        return config

    def read_paper_weight_per_assignment(self) -> Dict[str, float]:
        # In the config you either can express the weight per assignment as the
        # actual mass or you can express the width of paper per assignment (to make measurement easier)

        paper_weight_per_assignment = self.try_read_specified_weight_per_assignment()

        if paper_weight_per_assignment == {}:
            paper_width_section = self.config["PAPER_WIDTH_PER_ASSIGNMENT"]

            paper_weight_per_assignment = {
                assignment.upper(): self.weight_per_height_unit * float(width)
                for assignment, width in paper_width_section.items()
            }

        return paper_weight_per_assignment

    def get_absolute_best_combination(self) -> BinderCombination:
        # Running the program with a for loop I noticed something really strange:
        # best combination with 5 binders: [['ENG', 'HGE'], ['FR'], ['ESP', 'CAT', 'EMC'], ['HGF', 'SPC'], ['SES']]
        # best combination with 6 binders: [['ENG', 'HGE'], ['FR'], ['ESP', 'CAT', 'EMC'], ['HGF', 'SPC'], ['SES'], []]
        # Huh? There is no sixth binder... The best combination is given with only 5 binders!
        # Humans may think that the best combination is the one where each assignment is on a different binder, but test tells us the opposite.
        # Some assignments are so light-weight, that it would be heavier carrying the weight of an empty binder + the weight of the assignment than carrying the weight of other assignments too

        n = 1
        prior_best_combination = BinderCombination(inf, [])
        while True:
            current_best_combination = self.get_best_combination_for_n_binders(n)

            # If the combination has an empty binder, it means that the absolute best combination was the one before
            if [] in current_best_combination.assignments_combination:
                return prior_best_combination

            prior_best_combination = current_best_combination
            n += 1

    def get_best_combination_for_n_binders(
        self, number_of_binders: int, give_worse_combination: bool = False
    ) -> BinderCombination:
        best_combination = BinderCombination(inf, [])
        worse_combination = BinderCombination(0, [])

        # Loop through all the possible partitions of the assignments according to the number of binders:
        # Ex with 2 binders: [['ENG', 'MATH'], []] : The first binder will contain English and Math and the second one won't contain anything
        #                    [['ENG'], ['MATH']] : The first binder will contain English and the second one Math
        for assignments_combination in get_partitions_of_list(
            self.binder_assignments, number_of_binders
        ):
            # Average carried weight with this combination according to the schedule in the config file
            average_carried_weight = (
                self.get_average_carried_weight_with_assignments_combination(
                    assignments_combination
                )
            )

            (
                best_combination,
                worse_combination,
            ) = self.change_worse_or_best_combination_if_needed(
                assignments_combination,
                average_carried_weight,
                best_combination,
                worse_combination,
            )

        return worse_combination if give_worse_combination else best_combination


    def try_read_specified_weight_per_assignment(self) -> Dict[str, float]:
        paper_weight_section = None
        try:
            paper_weight_section = self.config["PAPER_WEIGHT_PER_ASSIGNMENT"]
        except KeyError:
            return {}

        if list(paper_weight_section) == []:
            return {}

        paper_weight_per_assignment = {
            assignment.upper(): float(weight)
            for assignment, weight in paper_weight_section.items()
        }

        return paper_weight_per_assignment

    def read_weight_per_height_unit(self) -> float:
        section = self.config["GENERAL"]

        return float(section["WEIGHT_PER_HEIGHT_UNIT"])

    def read_schedule(self) -> list[list[list[list[str]]]]:
        # Contains a list of weeks (week: list)
        schedule = []

        week_n = 1
        while True:
            try:
                section = self.config[f"ASSIGNMENTS_PER_DAY_WEEK{week_n}"]
            except KeyError:
                break

            # Split the week in days themselves split in before_switches
            week = [
                day_schedule.split(" ") for day, day_schedule in dict(section).items()
            ]

            # Contains a list of days (day: a list that contains a list of
            # assignments_before_switches (assignments_before_switch: a list of
            # assignments (str))
            week = [[before_switch.split(",") for before_switch in day] for day in week]

            schedule.append(week)

            week_n += 1

        return schedule

    def change_worse_or_best_combination_if_needed(
        self,
        assignments_combination: list[list[str]],
        average_carried_weight: float,
        best_combination: BinderCombination,
        worse_combination: BinderCombination,
    ) -> tuple[BinderCombination, BinderCombination]:
        if average_carried_weight > worse_combination.average_carried_weight:
            worse_combination = BinderCombination(
                average_carried_weight, assignments_combination
            )
        elif average_carried_weight < best_combination.average_carried_weight:
            best_combination = BinderCombination(
                average_carried_weight, assignments_combination
            )

        return best_combination, worse_combination

    def get_average_carried_weight_with_assignments_combination(
        self, assignments_combination: list[list[str]]
    ) -> float:
        # It is a list of binders (dictionary).
        # each binder has an 'assignments' property: a list of the assignment it contains
        # and a 'weight' property: the weight of all the sheets of the assignments
        binders = self.get_binders_out_of_assignments_combination(
            assignments_combination
        )

        # Between every switch of books the carried_weight changes: we want
        # to store all the carried_weight of before every book switch to
        # make the average carried_weight
        carried_weights_before_switches = []
        for week in self.schedule:
            for day in week:
                for assignments_before_switch in day:
                    carried_weight = self.get_carried_weight_before_switch(
                        binders, assignments_before_switch
                    )

                    carried_weights_before_switches.append(carried_weight)

        average_carried_weight = sum(carried_weights_before_switches) / len(
            carried_weights_before_switches
        )

        return average_carried_weight

    def get_carried_weight_before_switch(
        self, binders: list[Binder], assignments_before_switch: list[str]
    ) -> float:
        # This set is going to contain the indexes of the
        # binders needed before the book switch
        binders_needed: set[int] = set()

        for assignment in assignments_before_switch:
            self.add_binder_index_if_needed(binders_needed, assignment, binders)

        # We have got the indexes of all the binders needed
        total_binders_weight = self.get_weight_of_binders_with_indexes(
            binders_needed, binders
        )

        return total_binders_weight

    def add_binder_index_if_needed(
        self, binders_needed: set[int], assignment: str, binders: list[Binder]
    ) -> None:
        binder_needed = self.get_index_of_binder_containing_assignment(
            assignment, binders
        )

        if binder_needed is not None:
            # As it is a set: it is going to contain unique
            # elements
            binders_needed.add(binder_needed)

    def get_binders_out_of_assignments_combination(
        self, all_assignments_combinations: list[list[str]]
    ) -> list[Binder]:
        binders = [
            Binder(assignments_combination, 0)
            for assignments_combination in all_assignments_combinations
        ]

        for binder in binders:
            weight = self.empty_binder_weight

            for assignment in binder.assignments:
                weight += self.weight_per_assignment[assignment]

            binder.weight = weight

        return binders

    def read_empty_binder_weight(self) -> float:
        section = self.config["GENERAL"]

        return float(section["EMPTY_BINDER_WEIGHT"])

    def read_binder_assignments(self) -> list[str]:
        assignments = list(self.weight_per_assignment.keys())

        return assignments

    def get_index_of_binder_containing_assignment(
        self, assignment: str, binders: list[Binder]
    ) -> Union[int, None]:
        for i, binder in enumerate(binders):
            if assignment in binder.assignments:
                return i
        else:
            return None

    def get_weight_of_binders_with_indexes(
        self, binders_indexes: set, binders: list[Binder]
    ) -> float:
        weight = 0
        for i in binders_indexes:
            weight += binders[i].weight

        return weight


if __name__ == "__main__":
    main()
