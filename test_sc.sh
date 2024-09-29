echo "Test search string:"

echo -n "+ string in function :"
if ./sc "found_string" | grep -q "checkCondition" ; then echo " pass" ; else echo " fail" ; fi

echo -n "+ string if nested for :"
if ./sc "Even number" | grep -q -e "if" -e "for" -e "checkCondition" ; then echo " pass" ; else echo " fail" ; fi

echo -n "+ string switch case nested if :"
if ./sc "x is 2" | grep -q -e "if" -e "switch" -e "case 2" ; then echo " pass" ; else echo " fail" ; fi

echo -n "+ string switch default nested if :"
if ./sc "x is less than 5" | grep -q -e "if" -e "switch" -e "default" ; then echo " pass" ; else echo " fail" ; fi