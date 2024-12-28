from evennia.utils.funcparser import FuncParser
from django.conf import settings

_FUNCPARSER = FuncParser(
    settings.FUNCPARSER_OUTGOING_MESSAGES_MODULES, raise_errors=True
)

#out=[]
#for test in ["$foo=$bar", "escapes \\= should work?","$1 = $2","$1=$2"]:
#
#    out.append(_FUNCPARSER.parse(test, strip=False, blah="Testattribte"))
teststr ="""
    $1=$2 is a fairly $long $string that $we $do 
    $not want $to count $against. However $it $seems
    $like $this $will $still $hit $the $recursion $limit
    $even $though $even $if $these $were $actually $functions
    $they $are $not $nested.
"""

teststr="$1 = $2"
teststr="""$-test
The end of the road.
\=  b"""

teststr="nick tell $1 $2=page $1=$2"
#print(teststr)
out = _FUNCPARSER.parse(teststr)
print(out)