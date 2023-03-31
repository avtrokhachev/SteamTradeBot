

def convert_to_dollars(raw_value: str) -> float:
    cur_val = [i for i in raw_value]
    ans = []
    for i in cur_val:
        if '0' <= i <= '9' or i in ',.':
            ans.append(i)
    ans = "".join(ans)
    ans = ans.replace(',', '.')
    if len(ans) == 0:
        ans = "0"
    return float(ans)