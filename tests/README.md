# Test bench for hashcat PR #5094

Builds small kernel sources with Metal's runtime compiler, the same call hashcat makes
(`newLibraryWithSource` with the build options as preprocessor macros), four ways:

- `reference`: Metal reads the included files itself. The headers in `bin/inc/` sit below the
  directory of `bin/metalc`, the one place macOS 27 lets the compiler read.
- `v1`, `v2`, `v3`: the include resolver of d284a3209, 828d4ccc7 and b86e6fcf8, taken verbatim from
  `src/ext_metal.m` by `extract.py` and compiled on its own by `harness.c` (with stand-ins for
  `hcmalloc ()` and friends) under AddressSanitizer and UBSan.

Every `file:line` a compiler message names is looked up in the source and printed with `ok`/`BAD`.

The scripts expect this folder at `/Users/Shared/hc5094-tests`:

```sh
cd /Users/Shared/hc5094-tests
git -C <hashcat> show d284a3209:src/ext_metal.m > ext_metal.v1.m
git -C <hashcat> show 828d4ccc7:src/ext_metal.m > ext_metal.v2.m
git -C <hashcat> show b86e6fcf8:src/ext_metal.m > ext_metal.v3.m
for v in v1 v2 v3; do
  python3 extract.py ext_metal.$v.m resolver_$v.inc
  clang -std=gnu99 -g -O1 -fsanitize=address,undefined -Wno-unused-function \
        -DRESOLVER="\"resolver_$v.inc\"" harness.c -o harness_$v
done
swiftc -O metalc.swift -o bin/metalc
python3 run_case.py review                # likewise m1_escape, m3_nul, m4_comment,
python3 run_case.py m6_macro USE_BS=1     # m5a_splice_include, m5b_splice_endif, m5c_splice_blanks
python3 run_case.py word-test
```
