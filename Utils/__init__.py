def get_numeric_suffix(i):
    if 0 < i < 4:
        return __numeric_suffix[i]
    return "th"


__numeric_suffix = {
    1: "st",
    2: "nd",
    3: "rd"
}