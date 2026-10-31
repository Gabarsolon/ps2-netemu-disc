"""Try the local public APP key vault with the existing SELF decoder.

No keys or Sony bytes are printed; decrypted output remains local_only.
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
source = (root / 'reference/buzz-netemu-build/selfdec.py').read_text()
source = source.replace('LoadSelfLV2Keys()', 'LoadSelfAPPKeys()')
source = source.replace('KEY_LV2', 'KEY_APP')
source = source.replace("assert self_type == 3, 'only LV2 type handled'", "assert self_type == 4, 'APP type required'")
# APP keys are selected by revision; vault versions name release endpoints,
# rather than a validity range enclosing every APP's declared version.
source = source.replace('k[0] <= app_ver <= k[1] and k[2] == keyrev', 'k[2] == keyrev')
exec(compile(source, str(root / 'reference/buzz-netemu-build/selfdec.py'), 'exec'))
