def sort_order(matches, odds):
    """
            Make sure matches and odds are in alphabeticla order
            :param matches:
            :param odds:
            :return:
            """
    if None in matches:
        match = f'{matches[0]} v {matches[1]}'
        return match, odds

    else:
        matches_sorted = sorted(matches)
        if matches_sorted != matches:
            odds = odds[::-1]

        # format matches into one string
        match = f'{matches_sorted[0]} v {matches_sorted[1]}'.replace("\'", "-")
        return match, odds
