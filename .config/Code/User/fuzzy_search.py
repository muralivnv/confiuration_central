from subprocess import check_output
from os import system
from sys import argv

search_type = "--search-file-content"
if len(argv) > 1:
  search_type = argv[1]

#################################################################
# filter setting
folders_to_ignore = ["CMakeFiles", "build", ".git"]
comment_line_ignore_re = "(\w+(?!^\s*(//|/\\*||#|<!--|;|-)))"
file_content_re = f"^\s*\w+{comment_line_ignore_re}"

# visual setting
fzf_cosmetic_opts = r"--color hl:221,hl+:74 --margin 1% --border"

def search_inside_files():
  folder_ignore_glob = ''.join(["--iglob \"!**/{}/**\" ".format(f) for f in folders_to_ignore])
  return f"rg --line-number --column {folder_ignore_glob} --pcre2 \"{file_content_re}\" | fzf --delimiter : --nth 3.. {fzf_cosmetic_opts}"

def search_filenames():
  folder_ignore_glob = ''.join(["--iglob \"!**/{}/**\" ".format(f) for f in folders_to_ignore])
  return f"rg {folder_ignore_glob} --files | fzf {fzf_cosmetic_opts}"
  
#################################################################

cmd = {}
cmd["--search-file-content"] = search_inside_files
cmd["--search-files"]        = search_filenames

try:
  file = check_output(cmd[search_type](), shell=True)
  file = file.decode("utf-8")
  file = ':'.join(file.split(':')[0:3])
  system("code -g {0}".format(file))
except KeyError:
  print(f"unknown command {search_type}")
except:
  pass
