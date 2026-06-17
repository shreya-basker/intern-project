from copy import deepcopy


def deep_merge(dict1, dict2):
    result = deepcopy(dict1)  # stores original value of dict1
    for key, value in dict2.items():
        # Case 1 : Both values are nested dictionaries, they are merged recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        # Case 2: If only one or both of them are not nested dict -> prevents overwriting
        elif key in result:
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        else:
            result[key] = deepcopy(value)
    return result


def main():
    dict1 = {"info": {"name": "Shreya", "age": 23}, "metadata": {"id": 201}}
    dict2 = {"info": {"skills": "SQL", "location": "New York"}, "metadata": {"id": 202}}
    merged_profile = deep_merge(dict1, dict2)
    import pprint

    pprint.pprint(merged_profile)


if __name__ == "__main__":
    main()
