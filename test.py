import re

LINKS_SUB = re.compile(r"\|lc(.*?)(?:\|lh(.*))?\|lt(.*?)\|le", re.DOTALL)

#text='|lc a|b|c |lh e|f|g |ltblah|le'
text='|lc say hi|ltblah|le'

def parse_send(matches):
    
    commands = matches.group(1)
    hints = matches.group(2)
    text = matches.group(3)

    print(f"commands {commands}. {'|' in commands}")
    print(f"hints {hints}")
    print(f"text {text}")

    # Must be an mxp MENU
    if '|' in commands:
        hintstr=None
        if hints:
            hintstr=f'hints="{hints.strip()}"'

        return f'<SEND "{commands.strip()}" {hintstr}>{text}</SEND>'    
    return f'<SEND HREF="{commands}">{text}</SEND>'

text = re.sub(LINKS_SUB,parse_send,text)
print(text)
# if match:
#     print(f"Group 1 (commands): {match.group(1)}")
#     print(f"Group 2 (hints): {match.group(2)}")
#     print(f"Group 3 (link text): {match.group(3)}")
# else:
#     print("No match.")