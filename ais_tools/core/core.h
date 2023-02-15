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
char * unsafe_strcpy(char * dest, const char * dest_end, const char * src);
size_t safe_strcpy(char * __restrict dst, const char * __restrict src, size_t dsize);

// checksum functions
int checksum(const char *s);
char* checksum_str(char * dst, const char* src, size_t dsize);
bool is_checksum_valid(char* s);

// tagblock functions
int join_tagblock(char* buffer, size_t buf_size, const char* tagblock_str, const char* nmea_str);
int split_tagblock(char* message, const char** tagblock, const char** nmea);


// Module methods
PyObject * method_compute_checksum(PyObject *module, PyObject *args);
PyObject * method_compute_checksum_str(PyObject *module, PyObject *args);
PyObject * method_is_checksum_valid(PyObject *module, PyObject *args);
PyObject * method_join_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs);
PyObject * method_split_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs);
PyObject * method_decode_tagblock(PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_encode_tagblock(PyObject *module, PyObject *const *args, Py_ssize_t nargs);
