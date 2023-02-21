#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "tagblock.h"


int update_tagblock(char * dest, size_t dest_size, char* message, PyObject * dict)
{
    const char* tagblock_str;
    const char* nmea_str;
    char tagblock_buffer[MAX_TAGBLOCK_STR_LEN];
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    int num_fields = 0;

    split_tagblock(message, &tagblock_str, &nmea_str);

    if (safe_strcpy(tagblock_buffer, tagblock_str, ARRAY_LENGTH(tagblock_buffer)) >= ARRAY_LENGTH(tagblock_buffer))
        return FAIL_STRING_TOO_LONG;

    num_fields = split_fields(tagblock_buffer, fields, ARRAY_LENGTH(fields));
    if (num_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    struct TAGBLOCK_FIELD update_fields[MAX_TAGBLOCK_FIELDS];
    int num_update_fields = 0;
    char value_buffer[MAX_VALUE_LEN];
    num_update_fields = encode_fields(dict, update_fields, ARRAY_LENGTH(update_fields),
                                      value_buffer, ARRAY_LENGTH(value_buffer));
    if (num_update_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    num_fields = merge_fields(fields, num_fields, ARRAY_LENGTH(fields), update_fields, num_update_fields);
    if (num_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    char updated_tagblock_str[MAX_TAGBLOCK_STR_LEN];
    join_fields(fields, num_fields, updated_tagblock_str, ARRAY_LENGTH(updated_tagblock_str));

    int msg_len = join_tagblock(dest, dest_size, updated_tagblock_str, nmea_str);
    if (msg_len < 0)
        return FAIL_STRING_TOO_LONG;

    return msg_len;
}


//// TODO: Move to methods.c
//static PyObject *
//method_update_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs)
//{
//    const char* str;
//    PyObject* dict;
//    char message[MAX_SENTENCE_LENGTH];
//    char updated_message[MAX_SENTENCE_LENGTH];
////    const char* tagblock_str;
////    const char* nmea_str;
//
//
//    if (nargs != 2)
//        return PyErr_Format(PyExc_TypeError, "update expects 2 arguments");
//
//    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
//    dict = args[1];
//
//    if (safe_strcpy(message, str, ARRAY_LENGTH(message)) >= ARRAY_LENGTH(message))
//        return PyErr_Format(PyExc_ValueError, ERR_NMEA_TOO_LONG);
//
//    int message_len = update_tagblock(updated_message);
//
//    if (message_len < 0)
//        switch(message_len)
//        {
//            case FAIL_STRING_TOO_LONG:
//                return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);
//            case FAIL_TOO_MANY_FIELDS:
//                return PyErr_Format(PyExc_ValueError, ERR_TOO_MANY_FIELDS);
//            default:
//                return PyErr_Format(PyExc_ValueError, ERR_UNKNOWN);
//        }
//
//    return PyUnicode_FromString(updated_message);
//
//}
//    split_tagblock(message, &tagblock_str, &nmea_str);


//    char tagblock_buffer[MAX_TAGBLOCK_STR_LEN];
//    if (safe_strcpy(tagblock_buffer, tagblock_str, ARRAY_LENGTH(tagblock_buffer)) >= ARRAY_LENGTH(tagblock_buffer))
//        return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);


//    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
//    int num_fields = 0;
//    num_fields = split_fields(tagblock_buffer, fields, ARRAY_LENGTH(fields));
//    if (num_fields < 0)
//        return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_DECODE);


//    struct TAGBLOCK_FIELD update_fields[MAX_TAGBLOCK_FIELDS];
//    int num_update_fields = 0;
//    char value_buffer[MAX_VALUE_LEN];
//    num_update_fields = encode_fields(dict, update_fields, ARRAY_LENGTH(update_fields),
//                                      value_buffer, ARRAY_LENGTH(value_buffer));
//    if (num_update_fields < 0)
//        return PyErr_Format(PyExc_ValueError, ERR_TOO_MANY_FIELDS);


//    num_fields = merge_fields(fields, num_fields, ARRAY_LENGTH(fields), update_fields, num_update_fields);
//    if (num_fields < 0)
//        return PyErr_Format(PyExc_ValueError, ERR_TOO_MANY_FIELDS);


//    char updated_tagblock_str[MAX_TAGBLOCK_STR_LEN];
//    join_fields(fields, num_fields, updated_tagblock_str, ARRAY_LENGTH(updated_tagblock_str));
//
//    int msg_len = join_tagblock(updated_message, ARRAY_LENGTH(updated_message), updated_tagblock_str, nmea_str);
//    if (msg_len < 0)
//        return PyErr_Format(PyExc_ValueError, ERR_NMEA_TOO_LONG);


