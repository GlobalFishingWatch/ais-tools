/* AIS Tools core functions implemented in C */

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */

#define SUCCESS 0
#define FAIL -1
#define FAIL_STRING_TOO_LONG -101
#define FAIL_TOO_MANY_FIELDS -102


#define ARRAY_LENGTH(array) (sizeof((array))/sizeof((array)[0]))

#define ERR_TAGBLOCK_DECODE    "Unable to decode tagblock string"
#define ERR_TAGBLOCK_TOO_LONG  "Tagblock string too long"
#define ERR_TOO_MANY_FIELDS    "Too many fields"
#define ERR_NMEA_TOO_LONG      "NMEA string too long"
#define ERR_UNKNOWN            "Unknown error"

#define MAX_TAGBLOCK_FIELDS  8         // max number of fields allowed in a tagblock
#define MAX_TAGBLOCK_STR_LEN  1024     // max length of a tagblock string
#define MAX_KEY_LEN  32                // max length of a single key in a tagblock
#define MAX_VALUE_LEN  256             // max length of a single value in a tagblock
#define MAX_SENTENCE_LENGTH 1024       // max length of a single nmea sentence (tagblock + AIVDM)

#define TAGBLOCK_SEPARATOR "\\"
#define CHECKSUM_SEPARATOR "*"
#define FIELD_SEPARATOR ","
#define KEY_VALUE_SEPARATOR ":"
#define GROUP_SEPARATOR "-"
#define AIVDM_START "!"
#define EMPTY_STRING ""


// string copy utils
char * unsafe_strcpy(char * __restrict dest, const char * __restrict est_end, const char * __restrict src);
size_t safe_strcpy(char * __restrict dst, const char * __restrict src, size_t dsize);
