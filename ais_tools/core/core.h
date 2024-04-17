/* AIS Tools core functions implemented in C */

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */

#define ARRAY_LENGTH(array) (sizeof((array))/sizeof((array)[0]))
#define MAX_SENTENCE_LENGTH 1024       // max length of a single nmea sentence (tagblock + AIVDM)

// string copy utils
char * unsafe_strcpy(char * __restrict dest, const char * __restrict est_end, const char * __restrict src);
size_t safe_strcpy(char * __restrict dst, const char * __restrict src, size_t dsize);
