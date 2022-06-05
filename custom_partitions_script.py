from typing import Generator
from copy import deepcopy

def get_partitions_of_list(items_to_partition : list, wanted_subsets_number : int) -> Generator[list, None, None]:
    # Cannot do [[]] * wanted_subsets_number
    # because believe it or not, all the children will be the same list (due to pointer manipulation)
    # [[], [], ...]
    modified_list : list = [[] for _ in range(wanted_subsets_number)]


    max_division = len(items_to_partition)
    # Size of each subset must
    # be less than the number of elements
    if wanted_subsets_number <= 0:
        raise ValueError(f'Cannot divide by {wanted_subsets_number} of subsets')
    elif wanted_subsets_number > max_division:
        raise ValueError(f'Cannot divide into {wanted_subsets_number}, maximum is {max_division}')
    elif wanted_subsets_number == 1:
        yield [items_to_partition]


    yield from all_ways_to_partition(
        items_to_partition=items_to_partition,
        number_of_elements_of_current_list=0,
        number_of_elements_of_final_list=len(items_to_partition),
        wanted_subsets_number=wanted_subsets_number,
        modified_list=modified_list
    )

def all_ways_to_partition(items_to_partition: list, number_of_elements_of_current_list: int, number_of_elements_of_final_list : int, wanted_subsets_number : int, modified_list : list) -> Generator[list[ list[str]], None, None]:
    # If all the items to partition are contained in the current combination, it
    # is a valid final partition
    if number_of_elements_of_current_list == number_of_elements_of_final_list:
        yield deepcopy(modified_list)  # Make sure there aren't pointer problems
    else:
        # This is the way we pass the same item_to_partition to different subsets
        # when all the different partitions of the tree have been explored
        for current_subset_index in range(wanted_subsets_number):
            perform_next_partition_variation(
                modified_list,
                current_subset_index,
                items_to_partition,
                number_of_elements_of_current_list
            )

            # Recursion
            yield from all_ways_to_partition(
                items_to_partition,
                number_of_elements_of_current_list + 1,
                number_of_elements_of_final_list, wanted_subsets_number,
                modified_list
            )

            # Remove last element added to the current subset (thanks to the
            # recursion, this will lead to the creation of the other partitions)
            # (ex: [['a', 'b']] -> [['a']] -> (the next for loop iteration of
            # the previous recursion call) [['a'], ['b']])
            modified_list[current_subset_index] = modified_list[current_subset_index][:-1]

            # We do not want to repeat partitions.
            # Because the empty subsets are given at the beginning, we do
            # not want to repeat those empty subsets that will lead to the
            # repetition of other partitions
            if modified_list[current_subset_index] == []:
                break

def perform_next_partition_variation(modified_list: list, current_subset_index: int, items_to_partition: list, number_of_elements_of_current_list: int) -> None:
    next_character_to_include = items_to_partition[number_of_elements_of_current_list]

    # As list's pointers are passed as arguments we can change the original list
    # inside another function
    modified_list[current_subset_index].append(next_character_to_include)