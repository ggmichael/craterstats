#  Copyright (c) 2026, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import sys

def get_documents_path():
    if sys.platform.startswith("win"):
        import ctypes
        from ctypes import wintypes

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0

        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
        )
        return buf.value
    else:
        # macOS / Linux
        return os.path.join(os.path.expanduser("~"), "Documents")