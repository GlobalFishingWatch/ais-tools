// tagblock module

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */
#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include "checksum.h"


#define SUCCESS 0
#define FAIL -1

const size_t MAX_TAGBLOCK_FIELDS = 8;
const size_t MAX_TAGBLOCK_STR_LEN = 1024;
const size_t MAX_KEY_LEN = 32;
const size_t MAX_VALUE_LEN = 256;
const char * CHECKSUM_SEPARATOR = "*";
const char * FIELD_SEPARATOR = ",";
const char * KEY_VALUE_SEPARATOR = ":";
const char * GROUP_SEPARATOR = "-";

struct TAGBLOCK_FIELD
{
    char key[2];
    const char* value;
};

#define TAGBLOCK_TIMESTAMP     "tagblock_timestamp"
#define TAGBLOCK_DESTINATION   "tagblock_destination"
#define TAGBLOCK_LINE_COUNT    "tagblock_line_count"
#define TAGBLOCK_RELATIVE_TIME "tagblock_relative_time"
#define TAGBLOCK_STATION       "tagblock_station"
#define TAGBLOCK_TEXT          "tagblock_text"
#define TAGBLOCK_SENTENCE      "tagblock_sentence"
#define TAGBLOCK_GROUPSIZE     "tagblock_groupsize"
#define TAGBLOCK_ID            "tagblock_id"
#define CUSTOM_FIELD_PREFIX    "tagblock_"
#define TAGBLOCK_GROUP         "g"

#define ERR_TAGBLOCK_DECODE    "Unable to decode tagblock string"
#define ERR_TAGBLOCK_TOO_LONG  "Tagblock string too long"
#define ERR_TOO_MANY_FIELDS    "Too many fields"

typedef struct {char short_key[2]; const char* long_key;} KEY_MAP;
static KEY_MAP key_map[] = {
    {"c", TAGBLOCK_TIMESTAMP},
    {"d", TAGBLOCK_DESTINATION},
    {"n", TAGBLOCK_LINE_COUNT},
    {"r", TAGBLOCK_RELATIVE_TIME},
    {"s", TAGBLOCK_STATION},
    {"t", TAGBLOCK_TEXT}
};

static const char* group_field_keys[3] = {TAGBLOCK_SENTENCE, TAGBLOCK_GROUPSIZE, TAGBLOCK_ID};

const char* lookup_long_key(const char *short_key)
{
    for (size_t i = 0; i < ARRAY_LENGTH(key_map); i++)
        if (0 == strcmp(key_map[i].short_key, short_key))
            return key_map[i].long_key;
    return NULL;
}

const char* lookup_short_key(const char* long_key)
{
    for (size_t i = 0; i < ARRAY_LENGTH(key_map); i++)
        if (0 == strcmp(key_map[i].long_key, long_key))
            return key_map[i].short_key;
    return NULL;
}

size_t lookup_group_field_key(const char* long_key)
{
    for (size_t i = 0; i < ARRAY_LENGTH(group_field_keys); i++)
        if (0 == strcmp(long_key, group_field_keys[i]))
            return i + 1;
    return 0;
}

void extract_custom_short_key(char* buffer, size_t buf_size, const char* long_key)
{
    size_t prefix_len = ARRAY_LENGTH(CUSTOM_FIELD_PREFIX) - 1;

    if (0 == strncmp(CUSTOM_FIELD_PREFIX, long_key, prefix_len))
        strlcpy(buffer, &long_key[prefix_len], buf_size);
    else
        strlcpy(buffer, long_key, buf_size);
}

void init_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields)
{
    for (size_t i = 0; i < num_fields; i++)
    {
        fields[i].key[0] = '\0';
        fields[i].value = NULL;
    }
}

// copy str into dest up to end
// return a pointer to the position immediately after the last position written in dest
// does not copy the null terminator from str
static char *unsafe_strcat(char *dest, const char *end, const char *str)
{
    while (dest < end && *str)
        *dest++ = *str++;
    return dest;
}

// split a tagblock string with structure
//   k:value,k:value*cc
int split_fields(char* tagblock_str, struct TAGBLOCK_FIELD* fields, int max_fields)
{
    int idx = 0;
    char * field_save_ptr = NULL;
    char * field;

    char * key_value_save_ptr = NULL;

    // strip off the checksum if present
    field_save_ptr = strstr(tagblock_str, CHECKSUM_SEPARATOR);
    if (field_save_ptr != NULL)
        *field_save_ptr = '\0';

    // make sure we have something to decode
    if (!tagblock_str || !*tagblock_str)
        return 0;

    // get the first comma delimited field
    field = strtok_r(tagblock_str, FIELD_SEPARATOR, &field_save_ptr);
    while (field && *field && idx < max_fields)
    {
        // for each field, split into key part and value part
        const char* key = strtok_r(field, KEY_VALUE_SEPARATOR, &key_value_save_ptr);
        const char* value = strtok_r(NULL, KEY_VALUE_SEPARATOR, &key_value_save_ptr);

        // if we don't have both key and value, then fail
        if (key && value)
        {
            strlcpy(fields[idx].key, key, ARRAY_LENGTH(fields[idx].key));
            fields[idx].value = value;
            idx++;
        }
        else
            return FAIL;

        // advance to the next field
        field = strtok_r(NULL, FIELD_SEPARATOR, &field_save_ptr);
    }
    return idx;
}

// TODO: need a return value that indicates the string is too long
size_t join_fields(const struct TAGBLOCK_FIELD* fields, size_t num_fields, char* tagblock_str, size_t buf_size)
{
    const char * end = tagblock_str + buf_size - 4;
    size_t last_field_idx = num_fields - 1;
    char * ptr = tagblock_str;
    char checksum_str[3];

    for (size_t idx = 0; idx < num_fields; idx++)
    {
        ptr = unsafe_strcat(ptr, end, fields[idx].key);
        ptr = unsafe_strcat(ptr, end, KEY_VALUE_SEPARATOR);
        ptr = unsafe_strcat(ptr, end, fields[idx].value);
        if (idx < last_field_idx)
        {
            ptr = unsafe_strcat(ptr, end, FIELD_SEPARATOR);
        }
    }
    *ptr++ = '\0';  // very important!  unsafe_strcat does not add a null at the end of the string

    // TODO: use unsafe_strcat instead of strcat
    _checksum_str(tagblock_str, checksum_str);

    strcat(tagblock_str, CHECKSUM_SEPARATOR);
    strcat(tagblock_str, checksum_str);

    return strlen(tagblock_str);
}

int decode_timestamp_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    char * end;

    long value = strtol(field->value, &end, 10);
    if (errno || *end)
        return FAIL;

    if (value > 40000000000)
        value = value / 1000;
    PyDict_SetItemString(dict, key, PyLong_FromLong(value));
    return SUCCESS;
}

int decode_int_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    char* end;

    long value = strtol(field->value, &end, 10);
    if (errno || *end)
        return FAIL;

    PyDict_SetItemString(dict, key, PyLong_FromLong(value));

    return SUCCESS;
}

int decode_text_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    PyDict_SetItemString(dict, key, PyUnicode_FromString(field->value));

    return SUCCESS;
}

int decode_group_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    size_t idx = 0;
    char * save_ptr = NULL;
    long values[ARRAY_LENGTH(group_field_keys)];
    char buffer[MAX_VALUE_LEN];

    if (strlcpy(buffer, field->value, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
        return FAIL;

    char * f = strtok_r(buffer, GROUP_SEPARATOR, &save_ptr);
    while (f && idx < ARRAY_LENGTH(values))
    {
        char* end;
        values[idx++] = strtol(f, &end, 10);
        if (errno || *end)
            return FAIL;

        f = strtok_r(NULL, GROUP_SEPARATOR, &save_ptr);
    }
    if (idx == ARRAY_LENGTH(values))
    {
        for (idx = 0; idx < ARRAY_LENGTH(values); idx++)
            PyDict_SetItemString(dict, group_field_keys[idx], PyLong_FromLong(values[idx]));
        return SUCCESS;
    }

    return FAIL;
}

int decode_custom_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    char custom_key[MAX_KEY_LEN];
    snprintf(custom_key, ARRAY_LENGTH(custom_key), "%s%s", CUSTOM_FIELD_PREFIX, field->key);
    PyDict_SetItemString(dict, custom_key, PyUnicode_FromString(field->value));

    return SUCCESS;
}

size_t encode_group_fields(char* buffer, size_t buf_size, struct TAGBLOCK_FIELD* group_fields)
{
    const char * end = buffer + buf_size - 1;
    char * ptr = buffer;

    for (size_t i = 0; i < ARRAY_LENGTH(group_field_keys); i++)
    {
        // make sure that all values are non-empty
        if (group_fields[i].value == NULL)
            return 0;

        ptr = unsafe_strcat(ptr, end, group_fields[i].value);
        if (i < ARRAY_LENGTH(group_field_keys) - 1)
            ptr = unsafe_strcat(ptr, end, GROUP_SEPARATOR);
    }
    *ptr++ = '\0';   // very important!  unsafe_strcat does not add a null at the end of the string

    return ptr - buffer;
}

static PyObject *
tagblock_decode(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    const char *param;
    char tagblock_str[MAX_TAGBLOCK_STR_LEN];
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    int num_fields = 0;
    int status = SUCCESS;

    if (nargs != 1)
        return NULL;

    param = PyUnicode_AsUTF8(PyObject_Str(args[0]));

    if (strlcpy(tagblock_str, param, ARRAY_LENGTH(tagblock_str)) >= ARRAY_LENGTH(tagblock_str))
    {
        PyErr_SetString(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);
        return NULL;
    }

    PyObject* dict = PyDict_New();

    num_fields = split_fields(tagblock_str, fields, ARRAY_LENGTH(fields));
    if (num_fields < 0)
        status = FAIL;

    for (int i = 0; i < num_fields && status==SUCCESS; i++)
    {
        struct TAGBLOCK_FIELD* field = &fields[i];
        const char* key = field->key;

        switch(key[0])
        {
            case 'c':
                status = decode_timestamp_field(field, dict);
                break;
            case 'd':
            case 's':
            case 't':
                status = decode_text_field(field, dict);
                break;
            case 'g':
                status = decode_group_field(field, dict);
                break;
            case 'n':
            case 'r':
                status = decode_int_field(field, dict);
                break;
            default:
                status = decode_custom_field(field, dict);
        }
    }

    if (status == SUCCESS)
        return dict;
    else
    {
        PyErr_SetString(PyExc_ValueError, ERR_TAGBLOCK_DECODE);
        return NULL;
    }
}

int encode_fields(PyObject* dict, struct TAGBLOCK_FIELD* fields, size_t max_fields, char* buffer, size_t buf_size)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    size_t field_idx = 0;
    struct TAGBLOCK_FIELD group_fields[ARRAY_LENGTH(group_field_keys)];

    init_fields (group_fields, ARRAY_LENGTH(group_fields));

    while (PyDict_Next(dict, &pos, &key, &value))
    {
        if (field_idx == max_fields)
            return FAIL;    // no more room in fields

        const char* key_str = PyUnicode_AsUTF8(PyObject_Str(key));
        const char* value_str = PyUnicode_AsUTF8(PyObject_Str(value));

        size_t group_ordinal = lookup_group_field_key(key_str);
        if (group_ordinal > 0)
        {
            group_fields[group_ordinal - 1].value = value_str;
        }
        else
        {
            const char* short_key = lookup_short_key (key_str);

            if (short_key)
                strlcpy(fields[field_idx].key, short_key, ARRAY_LENGTH(fields[field_idx].key));
            else
                extract_custom_short_key(fields[field_idx].key, ARRAY_LENGTH(fields[field_idx].key), key_str);

            fields[field_idx].value = value_str;
            field_idx++;
        }
    }

    // encode group field and add it to the field list
    // check the return code to see if there is a complete set of group fields
    if (encode_group_fields(buffer, buf_size, group_fields))
    {
        if (field_idx >= max_fields)
            return FAIL;        // no more room to add another field

        strlcpy(fields[field_idx].key, TAGBLOCK_GROUP, ARRAY_LENGTH(fields[field_idx].key));
        fields[field_idx].value = buffer;
        field_idx++;
    }

    return field_idx;
}


int merge_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields, size_t max_fields,
                  struct TAGBLOCK_FIELD* update_fields, size_t num_update_fields)
{
    for (size_t update_idx = 0; update_idx < num_update_fields; update_idx++)
    {
        char* key = update_fields[update_idx].key;

        size_t fields_idx = 0;
        while (fields_idx < num_fields)
        {
            if (0 == strcmp(key, fields[fields_idx].key))
                break;
            fields_idx++;
        }
        if (fields_idx == num_fields)
        {
            if (num_fields < max_fields)
                num_fields++;
            else
                return FAIL;
        }

        fields[fields_idx] = update_fields[update_idx];


//
//        for (size_t fields_idx = 0; fields_idx < num_fields; fields_idx++)
//        {
//            if (0 == strcmp(key, fields[fields_idx].key))
//            {
//                // found a matching field. Replace the value
//                fields[fields_idx].value = update_fields[update_idx].value;
//                break;
//            }
//        }
//        // no matching field found. Append to the end if there is room
//        if (num_fields < max_fields)
//            fields[num_fields++] = update_fields[update_idx];
//        else
//            return FAIL;
    }

    return num_fields;
}



static PyObject *
tagblock_encode(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{

    PyObject *dict;
//    , *key, *value;
//    Py_ssize_t pos = 0;

    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
//    struct TAGBLOCK_FIELD group_fields[ARRAY_LENGTH(group_field_keys)];

    init_fields (fields, ARRAY_LENGTH(fields));
//    init_fields (group_fields, ARRAY_LENGTH(group_fields));

//    size_t field_idx = 0;
    char tagblock_str[MAX_TAGBLOCK_STR_LEN];
//    char checksum_str[3];
    char value_buffer [MAX_VALUE_LEN];

    if (nargs != 1)
        return NULL;

    dict = args[0];

    int num_fields = encode_fields(dict, fields, ARRAY_LENGTH(fields), value_buffer, ARRAY_LENGTH(value_buffer));
    if (num_fields < 0)
    {
        PyErr_SetString(PyExc_ValueError, ERR_TOO_MANY_FIELDS);
        return NULL;
    }

//    while (PyDict_Next(dict, &pos, &key, &value) && field_idx < ARRAY_LENGTH(fields) ) {
//        const char* key_str = PyUnicode_AsUTF8(PyObject_Str(key));
//        const char* value_str = PyUnicode_AsUTF8(PyObject_Str(value));
//
//        size_t group_ordinal = lookup_group_field_key(key_str);
//        if (group_ordinal > 0)
//        {
//            group_fields[group_ordinal - 1].value = value_str;
//        }
//        else
//        {
//            const char* short_key = lookup_short_key (key_str);
//
//            if (short_key)
//                strlcpy(fields[field_idx].key, short_key, ARRAY_LENGTH(fields[field_idx].key));
//            else
//                extract_custom_short_key(fields[field_idx].key, ARRAY_LENGTH(fields[field_idx].key), key_str);
//
//            fields[field_idx].value = value_str;
//            field_idx++;
//        }
//    }
//
//    // encode group field and add it to the field list
//    if (field_idx < ARRAY_LENGTH(fields))
//    {
//        // check the return code to see if there is a complete set of group fields
//        if (encode_group_fields(group_field_value, ARRAY_LENGTH(group_field_value), group_fields))
//        {
//            strlcpy(fields[field_idx].key, TAGBLOCK_GROUP, ARRAY_LENGTH(fields[field_idx].key));
//            fields[field_idx].value = group_field_value;
//            field_idx++;
//        }
//    }

    join_fields(fields, num_fields, tagblock_str, ARRAY_LENGTH(tagblock_str));

//    _checksum_str(tagblock_str, checksum_str);
//    strcat(tagblock_str, CHECKSUM_SEPARATOR);
//    strcat(tagblock_str, checksum_str);

    return PyUnicode_FromString(tagblock_str);
}


static PyObject *
tagblock_update(PyObject *module,  PyObject *const *args, Py_ssize_t nargs)
{
    const char* str;
    PyObject* dict;
    char tagblock_str[MAX_TAGBLOCK_STR_LEN];
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    int num_fields = 0;
    struct TAGBLOCK_FIELD update_fields[MAX_TAGBLOCK_FIELDS];
    int num_update_fields = 0;
    char value_buffer[MAX_VALUE_LEN];


//    int status = SUCCESS;

    if (nargs != 2)
    {
        PyErr_SetString(PyExc_TypeError, "update expects 2 arguments");
        return NULL;
    }

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    dict = args[1];

    if (strlcpy(tagblock_str, str, ARRAY_LENGTH(tagblock_str)) >= ARRAY_LENGTH(tagblock_str))
    {
        PyErr_SetString(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);
        return NULL;
    }

    num_fields = split_fields(tagblock_str, fields, ARRAY_LENGTH(fields));
    if (num_fields < 0)
    {
        PyErr_SetString(PyExc_ValueError, ERR_TAGBLOCK_DECODE);
        return NULL;
    }

    // TODO: return failure if (num_update_fields < 0)
    num_update_fields = encode_fields(dict, update_fields, ARRAY_LENGTH(update_fields),
                                      value_buffer, ARRAY_LENGTH(value_buffer));
    if (num_update_fields < 0)
    {
        PyErr_SetString(PyExc_ValueError, ERR_TOO_MANY_FIELDS);
        return NULL;
    }

    num_fields = merge_fields(fields, num_fields, ARRAY_LENGTH(fields), update_fields, num_update_fields);
    if (num_fields < 0)
    {
        PyErr_SetString(PyExc_ValueError, ERR_TOO_MANY_FIELDS);
        return NULL;
    }

    join_fields(fields, num_fields, tagblock_str, ARRAY_LENGTH(tagblock_str));

    return PyUnicode_FromString(tagblock_str);
}


static PyMethodDef tagblock_methods[] = {
    {"decode", (PyCFunction)(void(*)(void))tagblock_decode, METH_FASTCALL,
     "decode a tagblock string.  Returns a dict"},
    {"encode", (PyCFunction)(void(*)(void))tagblock_encode, METH_FASTCALL,
     "encode a tagblock string from a dict.  Returns a string"},
    {"update", (PyCFunction)(void(*)(void))tagblock_update, METH_FASTCALL,
     "update a tagblock string from a dict.  Returns a string"},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef tagblock_module = {
    PyModuleDef_HEAD_INIT,
    "_tagblock",
    NULL,
    -1,
    tagblock_methods
};

PyMODINIT_FUNC
PyInit__tagblock(void)
{
    return PyModule_Create(&tagblock_module);
}