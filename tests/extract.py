# extract.py <ext_metal.m> <out.inc>: the include resolver of src/ext_metal.m, as it is in that file
import sys
src = open(sys.argv[1], encoding="utf-8").read()
start = src.index("#define MTL_INCLUDE_DEPTH_MAX")
fn = src.index("static char *hc_mtlResolveIncludes")
end = src.index("\n}\n", fn) + 3
open(sys.argv[2], "w", encoding="utf-8").write(src[start:end])
