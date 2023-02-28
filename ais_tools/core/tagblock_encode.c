#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "tagblock.h"


size_t encode_group_fields(char* buffer, size_t buf_size, struct TAGBLOCK_FIELD* group_fields)
{
    const char * end = buffer + buf_size - 1;
    char * ptr = buffer;

    for (size_t i = 0; i < ARRAY_LENGTH(group_field_keys); i++)
    {
        // make sure that all values are non-empty
        if (group_fields[i].value == NULL)
            return 0;

        ptr = unsafe_strcpy(ptr, end, group_fields[i].value);
        if (i < ARRAY_LENGTH(group_field_keys) - 1)
            ptr = unsafe_strcpy(ptr, end, GROUP_SEPARATOR);
    }
    *ptr++ = '\0';   // very important!  unsafe_strcpy does not add a null at the end of the string

    return ptr - buffer;
}


int encode_fields(struct TAGBLOCK_FIELD* fields, size_t max_fields, PyObject* dict, char* buffer, size_t buf_size)
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

        int group_field_idx = lookup_group_field_key(key_str);
        if (group_field_idx >= 0)
        {
            group_fields[group_field_idx].value = value_str;
        }
        else
        {
            const char* short_key = lookup_short_key (key_str);

            if (short_key)
                safe_strcpy(fields[field_idx].key, short_key, ARRAY_LENGTH(fields[field_idx].key));
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

        safe_strcpy(fields[field_idx].key, TAGBLOCK_GROUP, ARRAY_LENGTH(fields[field_idx].key));
        fields[field_idx].value = buffer;
        field_idx++;
    }

    return field_idx;
}

int encode_tagblock(char * dest, PyObject *dict, size_t dest_buf_size)
{
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    char value_buffer [MAX_VALUE_LEN];

    init_fields (fields, ARRAY_LENGTH(fields));

    int num_fields = encode_fields(fields, ARRAY_LENGTH(fields), dict, value_buffer, ARRAY_LENGTH(value_buffer));
    if (num_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    int str_len = join_fields(dest, dest_buf_size, fields, num_fields);
    if (str_len < 0)
        return FAIL_STRING_TOO_LONG;
    return str_len;
}