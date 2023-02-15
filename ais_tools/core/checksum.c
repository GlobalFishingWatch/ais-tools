// checksum module

#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"

/*
 * Compute the checksum value of a string.  This is
 * computed by xor-ing the integer value of each character in the string
 * sequentially.
 */
int checksum(const char *s)
{
    int c = 0;
    while (*s)
      c = c ^ *s++;
    return c;
}

/*
 * Get the checksum value of a string as a 2-character hex string
 * This is always uppercase.  The destination buffer must be at least 3 chars
 * (one for the terminating null character)
 *
 * Returns a pointer to the destination buffer
 * Returns null  if the dest buffer is too small
 */
char* checksum_str(char * __restrict dst, const char* __restrict src, size_t dsize)
{
    if (dsize < 3)
        return NULL;

    int c = checksum(src);
    sprintf(dst, "%02X", c);
    return dst;
}
//
//char* checksum_str(const char * s, char* c_str)
//{
//    int c = checksum(s);
//    sprintf(c_str, "%02X", c);
//    return c_str;
//}

/*
 * Compute the checksum value of the given string and compare it to the checksum
 * that appears at the end of the string.
 * the checksum should be a 2 character hex value at the end separated by  a '*'
 *
 * For example:
 *    c:1000,s:old*5A
 *
 * If the string starts with any of these characrters ?!\ then the first character is ignored
 * for purposes of computing the checksum
 *
 * If no checksum is found at at the end of the string then the return is false
 *
 * Returns true if the checksum at the end of the string matches the computed checksum, else false
 *
 * NOTE: The given string will be modified to separate it into the body portion and the checksum portion
 */
bool is_checksum_valid(char* s)
{
  const char * skip_chars = "!?\\";
  const char separator = '*';

  char* body = s;
  char* c_str = NULL;
  char computed_checksum[3];

  if (*body && strchr(skip_chars, body[0]))
    body++;

  char* ptr = body;
  while (*ptr != '\0' && *ptr != separator)
      ptr++;

  if (*ptr == '*')
      *ptr++ = '\0';
  c_str = ptr;

  if (c_str == NULL || strlen(c_str) != 2)
    return false;

  checksum_str(computed_checksum, body, ARRAY_LENGTH(computed_checksum));
  return strcasecmp(c_str, computed_checksum) == 0;
}

//
//PyObject *
//core_compute_checksum(PyObject *module, PyObject *args)
//{
//    const char *str;
//    int c;
//
//    if (!PyArg_ParseTuple(args, "s", &str))
//        return NULL;
//    c = checksum(str);
//    return PyLong_FromLong(c);
//}
//
//PyObject *
//core_compute_checksum_str(PyObject *module, PyObject *args)
//{
//    const char *str;
//    char c_str[3];
//
//    if (!PyArg_ParseTuple(args, "s", &str))
//        return NULL;
//    checksum_str(c_str, str, ARRAY_LENGTH(c_str));
//    return PyUnicode_FromString(c_str);
//}
//
//PyObject *
//core_is_checksum_valid(PyObject *module, PyObject *args)
//{
//    char *str;
//    char buffer[MAX_SENTENCE_LENGTH];
//
//    if (!PyArg_ParseTuple(args, "s", &str))
//        return NULL;
//
//    if (safe_strcpy(buffer, str, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
//    {
//        PyErr_SetString(PyExc_ValueError, "String too long");
//        return NULL;
//    }
//
//    return is_checksum_valid(buffer) ? Py_True: Py_False;
//}

//
//static PyMethodDef checksum_methods[] = {
//    {"checksum", (PyCFunction)(void(*)(void))checksum_compute_checksum, METH_VARARGS,
//     "Compute checksum of a string. returns an integer value"},
//    {"checksumstr", (PyCFunction)(void(*)(void))checksum_compute_checksumstr, METH_VARARGS,
//     "Compute checksum of a string. returns a 2-character hex string"},
//    {"is_checksum_valid", (PyCFunction)(void(*)(void))checksum_is_checksum_valid, METH_VARARGS,
//     "Returns True if the given string is terminated with a valid checksum, else False"},
//    {NULL, NULL, 0, NULL}   /* sentinel */
//};
//
//static struct PyModuleDef checksum_module = {
//    PyModuleDef_HEAD_INIT,
//    "checksum",
//    NULL,
//    -1,
//    checksum_methods
//};
//
//PyMODINIT_FUNC
//PyInit_checksum(void)
//{
//    return PyModule_Create(&checksum_module);
//}