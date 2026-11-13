// Test harness: the include resolver of src/ext_metal.m, compiled on its own with stand-ins for the
// hashcat helpers it calls. RESOLVER names the extracted code of one version.
//
//   harness resolve <source> <include_dir>   print the source with its includes resolved
//   harness word-test                        call hc_mtlIncludeWord () with p past end

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>
#include <stdarg.h>
#include <sys/stat.h>

typedef uint32_t u32;

static void *hcmalloc (const size_t sz) { return calloc (sz, 1); }
static void *hcrealloc (void *ptr, const size_t oldsz, const size_t addsz)
{
  void *p = realloc (ptr, oldsz + addsz);
  if (p == NULL) return NULL;
  memset ((char *) p + oldsz, 0, addsz);
  return p;
}
static char *hcstrdup (const char *s) { return strdup (s); }
static void  hcfree (void *ptr) { if (ptr != NULL) free (ptr); }
static int   hc_asprintf (char **strp, const char *fmt, ...)
{
  va_list ap; va_start (ap, fmt); const int rc = vasprintf (strp, fmt, ap); va_end (ap); return rc;
}
static void  event_log_error (void *ctx, const char *fmt, ...)
{
  (void) ctx; va_list ap; va_start (ap, fmt); vfprintf (stderr, fmt, ap); va_end (ap); fputc ('\n', stderr);
}

#include RESOLVER

int main (int argc, char **argv)
{
  if ((argc == 2) && (strcmp (argv[1], "word-test") == 0))
  {
    // a 3 byte buffer, end at its end, p one byte past end

    char *buf = (char *) malloc (3);
    memcpy (buf, "abc", 3);
    const char *end = buf + 3;
    const char *p   = buf + 4;
    const char *r   = hc_mtlIncludeWord (p, end, "include");
    printf ("hc_mtlIncludeWord (p = end + 1) returned %s\n", (r == NULL) ? "NULL (refused)" : "a pointer (it read past the buffer)");
    free (buf);
    return 0;
  }

  if ((argc != 4) || (strcmp (argv[1], "resolve") != 0)) return 2;

  FILE *fp = fopen (argv[2], "rb");
  if (fp == NULL) return 2;
  fseek (fp, 0, SEEK_END); const long len = ftell (fp); fseek (fp, 0, SEEK_SET);
  char *src = (char *) calloc (len + 1, 1);
  fread (src, 1, len, fp); fclose (fp);

  char *out = hc_mtlResolveIncludes (NULL, src, argv[3]);
  if (out == NULL) return 1;
  fputs (out, stdout);
  free (out); free (src);
  return 0;
}
