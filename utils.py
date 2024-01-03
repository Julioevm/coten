def replace_items_in_list(target_list, start_index, items_to_replace):
    # Ensure the start_index + number of items does not exceed the length of the target_list
    end_index = min(start_index + len(items_to_replace), len(target_list))

    # Replace elements in target_list with elements from items_to_replace
    target_list[start_index:end_index] = items_to_replace[: end_index - start_index]

    return target_list
