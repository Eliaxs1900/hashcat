# run_case.py <case> [NAME=VALUE ...]
#
# Builds cases/<case>.cl with Metal's runtime compiler four ways and prints what the compiler says:
#   reference  Metal reads the included files itself (they sit below its executable, so it can)
#   v1         PR as first opened (d284a3209), includes resolved by hashcat
#   v2         + line count after #else/#elif/#endif (828d4ccc7)
#   v3         + hardening (this update)
# Every file:line a message names is looked up in the source, and the line's text is shown with
# whether it holds what the message is about. "word-test" calls hc_mtlIncludeWord () with p past end.
import os, re, subprocess, sys

T   = "/Users/Shared/hc5094-tests"
INC = T + "/bin/inc"
DIAG = re.compile(r"^(.*?):(\d+):(\d+): (error|warning): (.*?)( \[-W[^\]]*\])?$")

def word_test():
    for v in ("v1", "v2", "v3"):
        p = subprocess.run([f"{T}/harness_{v}", "word-test"], capture_output=True, text=True)
        err  = p.stderr.splitlines()
        asan = [l for l in err if "ERROR: AddressSanitizer" in l]
        if not asan:
            print(f"  {v}: {p.stdout.strip()}"); continue
        print(f"  {v}: " + asan[0].split("ERROR: ")[1].split(" on address")[0])
        for l in err:
            if l.startswith("READ of size") or ("in hc_mtlIncludeWord" in l and "#1" in l):
                print("        " + l.split(" thread")[0].strip()[:80])
        frames = [l.strip() for l in err if l.strip().startswith("#") and "hc_mtl" in l][:1]
        for l in frames:
            fn  = l.split(" in ", 1)[1].split(" ")[0]
            loc = l.rsplit(" ", 1)[-1].split("/")[-1]
            print(f"        in {fn} ({loc}), called with p one byte past end")

if sys.argv[1] == "word-test":
    word_test(); sys.exit(0)

case = sys.argv[1]
src = f"{T}/cases/{case}.cl"
macros = ["KERNEL_STATIC=1", f"INCLUDE_PATH={INC}", "XM2S(x)=#x", "M2S(x)=XM2S(x)"] + sys.argv[2:]

def source_line(name, n):
    path = src if name == "program_source" else os.path.join(INC, os.path.basename(name))
    lines = open(path, "rb").read().split(b"\n")
    return lines[n - 1].decode("utf-8", "replace") if 0 < n <= len(lines) else None

def diagnostics(path):
    out = subprocess.run([T + "/bin/metalc", path] + macros, capture_output=True, text=True).stdout
    res = []
    for l in out.splitlines():
        m = DIAG.match(l)
        if m:
            res.append((os.path.basename(m.group(1)), int(m.group(2)), m.group(4), m.group(5)))
        elif l.strip():
            res.append((None, 0, None, l.strip()))
    return res

def show(label, diags, ref):
    if label == "reference":
        same = "(Metal reads the included files itself)"
    else:
        same = "same as reference" if diags == ref else "DIFFERENT from reference"
    print(f"  {label:<9} {same}")
    for name, n, kind, msg in diags:
        if name is None:
            print(f"      {msg}"); continue
        text = source_line(name, n)
        holds = text is not None and (msg in text or ("null character" in msg and "\x00" in text)
                                      or ("#endif" in msg and "#endif" in text)
                                      or ("backslash and newline" in msg and re.search(r"\\[ \t]+$", text) is not None))
        shown = (text or "").replace("\x00", "\\0")
        print(f"      {name}:{n}: {kind}: {msg}")
        if text is None:
            print(f"        BAD {name} has no line {n}")
        else:
            print(f"        {'ok ' if holds else 'BAD'} line {n} of {name} is: {shown.strip()[:60]}")

print(f"== {case}.cl" + (f"  ({' '.join(sys.argv[2:])})" if sys.argv[2:] else ""))
for i, l in enumerate(open(src, encoding="utf-8").read().rstrip("\n").split("\n"), 1):
    print(f"  {i:>2} | {l}")
ref = diagnostics(src)
show("reference", ref, ref)
for v in ("v1", "v2", "v3"):
    out = f"{T}/out/{case}.{v}.cl"
    p = subprocess.run([f"{T}/harness_{v}", "resolve", src, INC], capture_output=True)
    open(out, "wb").write(p.stdout)
    asan = [l for l in p.stderr.decode("utf-8", "replace").splitlines() if "Sanitizer" in l or "runtime error" in l]
    show(v, diagnostics(out), ref)
    for l in asan[:2]:
        print(f"      SANITIZER: {l[:90]}")
