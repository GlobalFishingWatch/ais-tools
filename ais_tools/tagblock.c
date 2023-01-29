// tagblock module

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */
#include <Python.h>
#include <stdbool.h>
#include <string.h>

#define ARRAY_LENGTH(array) (sizeof((array))/sizeof((array)[0]))

const size_t MAX_TAGBLOCK_FIELDS = 8;
const size_t MAX_TAGBLOCK_STR_LEN = 1024;
const char * FIELD_SEPARATOR = ",";
const char * KEY_VALUE_SEPARATOR = ":";

struct TAGBLOCK_FIELD
{
  const char* key;
  const char* value;
};

// copy str into dest up to end
// return a pointer to the position immediately after the last position written in dest
// does not copy the null terminator from str
static char *util_cat(char *dest, const char *end, const char *str)
{
    while (dest < end && *str)
        *dest++ = *str++;
    return dest;
}

//size_t join_str(char *out_string, size_t out_bufsz, const char *delim, char **chararr)
//{
//    char *ptr = out_string;
//    char *strend = out_string + out_bufsz;
//    while (ptr < strend && *chararr)
//    {
//        ptr = util_cat(ptr, strend, *chararr);
//        chararr++;
//        if (*chararr)
//            ptr = util_cat(ptr, strend, delim);
//    }
//    return ptr - out_string;
//}

size_t split_fields(char* tagblock_str, struct TAGBLOCK_FIELD* fields, size_t max_fields)
{
  size_t idx = 0;
  char * field_save_ptr = NULL;
  char * field;

  char * key_value_save_ptr = NULL;

  field = strtok_r(tagblock_str, FIELD_SEPARATOR, &field_save_ptr);
  while (field && idx < max_fields)
  {
    fields[idx].key = strtok_r(field, KEY_VALUE_SEPARATOR, &key_value_save_ptr);
    fields[idx].value = strtok_r(NULL, KEY_VALUE_SEPARATOR, &key_value_save_ptr);
    idx++;
    field = strtok_r(NULL, FIELD_SEPARATOR, &field_save_ptr);
  }
  return idx;
}

size_t join_fields(const struct TAGBLOCK_FIELD* fields, size_t num_fields, char* tagblock_str, size_t buf_size)
{
  const char * end = tagblock_str + buf_size - 1;
  size_t last_field_idx = num_fields - 1;
  char * ptr = tagblock_str;

  for (size_t idx = 0; idx < num_fields; idx++)
  {
    ptr = util_cat(ptr, end, fields[idx].key);
    ptr = util_cat(ptr, end, KEY_VALUE_SEPARATOR);
    ptr = util_cat(ptr, end, fields[idx].value);
    if (idx < last_field_idx)
    {
      ptr = util_cat(ptr, end, FIELD_SEPARATOR);
    }
  }
  *ptr++ = '\0';
  return ptr - tagblock_str;
}


static PyObject *
tagblock_decode(PyObject *module, PyObject *args)
{
    char *tagblock_str;
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    size_t num_fields = 0;

    if (!PyArg_ParseTuple(args, "s", &tagblock_str))
        return NULL;

    num_fields = split_fields(tagblock_str, fields, ARRAY_LENGTH(fields));
    for (unsigned int i = 0; i < num_fields; i++)
    {
      printf("%s %s \n", fields[i].key, fields[i].value);
    }

    return PyUnicode_FromString("tags");
}

static PyMethodDef tagblock_methods[] = {
    {"decode", (PyCFunction)(void(*)(void))tagblock_decode, METH_VARARGS,
     "decode a tagblock string.  Returns a dict"},
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