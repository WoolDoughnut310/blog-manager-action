from re import compile

MARKDOWN_IMAGE = compile(r'!\[[^\]]*\]\((\w*?)\s*((?:\w+=)?"(?:.*[^"])")?\s*\)')
MARKDOWN_CODE_BLOCK = compile(r'```(?:.+)?#(.+)\n((?:.|\n)+?)\n+```')
