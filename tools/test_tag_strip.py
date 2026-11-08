import re

sample = """
<html><body><pre>
00100000  <font color=#ff0>81 </font>21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01  ! p=)  9)  +   <br>
</pre></body></html>
"""

# Strip tags completely
clean_text = re.sub(r'<[^>]+>', '', sample)
pattern = re.compile(r'([0-9A-F]{8})\s+((?:[0-9A-F]{2} ){16})')
m = pattern.findall(clean_text)
print("Matches with tags stripped:", len(m))
if m:
    print(m[0][0], m[0][1])
