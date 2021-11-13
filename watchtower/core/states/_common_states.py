from core.states.openSite import openSite
from core.states.getChapterListDynamic import getChapterListDynamic
from core.states.getChapterListStatic import getChapterListStatic
from core.states.parseChapterDynamic import parseChapterDynamic
from core.states.parseChapterStatic import parseChapterStatic



# What info is in data object:
# ============================
# [input]
# - "id"       -> Unique ID
# - "type"     -> TYPE object
# - "series"   -> target series info dict
# - "source"   -> source info dict
# - "driver"   -> webdriver object
# - "lock"     -> lock object used to synchronize multiple threads (v.imp. for webdriver interaction)
# - "response" -> scrapy.Response object
# - "url"      -> target url string
# - "state"    -> current state string
# - "meta"     -> response's metadata (not really needed, but just in case)
# [output]
# - "items"                list of dict
# 	- "chapter_name"    -> chapter title string
# 	- "chapter_id"      -> unique integer number
# 	- "chapter_content" -> list of objs
# - "requests"   list of dict
# 	- "driver"   -> put in meta (reference)
# 	- "lock"     -> put in meta (reference)
# 	- "url"      -> put in meta
# 	- "state"    -> put in meta
#   - "priority" -> put in Request
