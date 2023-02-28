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

    num_fields = split_fields(fields, tagblock_buffer, ARRAY_LENGTH(fields));
    if (num_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    struct TAGBLOCK_FIELD update_fields[MAX_TAGBLOCK_FIELDS];
    int num_update_fields = 0;
    char value_buffer[MAX_VALUE_LEN];
    num_update_fields = encode_fields(update_fields, ARRAY_LENGTH(update_fields), dict,
                                      value_buffer, ARRAY_LENGTH(value_buffer));
    if (num_update_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    num_fields = merge_fields(fields, num_fields, ARRAY_LENGTH(fields), update_fields, num_update_fields);
    if (num_fields < 0)
        return FAIL_TOO_MANY_FIELDS;

    char updated_tagblock_str[MAX_TAGBLOCK_STR_LEN];
    join_fields(updated_tagblock_str, ARRAY_LENGTH(updated_tagblock_str), fields, num_fields);

    int msg_len = join_tagblock(dest, dest_size, updated_tagblock_str, nmea_str);
    if (msg_len < 0)
        return FAIL_STRING_TOO_LONG;

    return msg_len;
}

