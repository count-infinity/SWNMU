def attribute_modifier_tbl():
    return {
        range(3,4): -2,    # 3
        range(4, 8): -1,     # 4-7
        range(8, 14): 0,    # 8-13
        range(14, 18): 1,   # 14-17
        range(18, 19): 2    # 18
    }


def lookup(value, table_func):
    tbl=table_func()
    for key_range, result in tbl.items():
        if value in key_range:
            return result
    return None