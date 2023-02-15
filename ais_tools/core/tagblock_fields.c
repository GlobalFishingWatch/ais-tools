#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include "core.h"
#include "tagblock.h"


typedef struct {char short_key[2]; const char* long_key;} KEY_MAP;
static KEY_MAP key_map[] = {
    {"c", TAGBLOCK_TIMESTAMP},
    {"d", TAGBLOCK_DESTINATION},
    {"n", TAGBLOCK_LINE_COUNT},
    {"r", TAGBLOCK_RELATIVE_TIME},
    {"s", TAGBLOCK_STATION},
    {"t", TAGBLOCK_TEXT}
};

const char* group_field_keys[3] = {TAGBLOCK_SENTENCE, TAGBLOCK_GROUPSIZE, TAGBLOCK_ID};

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
        safe_strcpy(buffer, &long_key[prefix_len], buf_size);
    else
        safe_strcpy(buffer, long_key, buf_size);
}

void init_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields)
{
    for (size_t i = 0; i < num_fields; i++)
    {
        fields[i].key[0] = '\0';
        fields[i].value = NULL;
    }
}

// split a tagblock string with structure
//   k:value,k:value
//   k:value,k:value*cc
//   \\k:value,k:value*cc\\other_stuff

int split_fields(char* tagblock_str, struct TAGBLOCK_FIELD* fields, int max_fields)
{
    int idx = 0;
    char * ptr;
    char * field_save_ptr = NULL;
    char * field;

    char * key_value_save_ptr = NULL;

    // skip leading tagblock delimiter
    if (*tagblock_str == *TAGBLOCK_SEPARATOR)
        tagblock_str++;

    // seek forward to find either the checksum, the next tagblock separator, or the end of the string.
    // Terminate the string at the first delimiter found
    for (ptr = tagblock_str; *ptr != *TAGBLOCK_SEPARATOR && *ptr != *CHECKSUM_SEPARATOR && *ptr != '\0'; ptr++);
    *ptr = '\0';

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
            safe_strcpy(fields[idx].key, key, ARRAY_LENGTH(fields[idx].key));
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


int join_fields(const struct TAGBLOCK_FIELD* fields, size_t num_fields, char* tagblock_str, size_t buf_size)
{
    const char * end = tagblock_str + buf_size - 1;
    size_t last_field_idx = num_fields - 1;
    char * ptr = tagblock_str;
    char checksum[3];

    for (size_t idx = 0; idx < num_fields; idx++)
    {
        ptr = unsafe_strcpy(ptr, end, fields[idx].key);
        ptr = unsafe_strcpy(ptr, end, KEY_VALUE_SEPARATOR);
        ptr = unsafe_strcpy(ptr, end, fields[idx].value);
        if (idx < last_field_idx)
        {
            ptr = unsafe_strcpy(ptr, end, FIELD_SEPARATOR);
        }
    }
    *ptr = '\0';  // very important!  unsafe_strcpy does not add a null at the end of the string

    checksum_str(checksum, tagblock_str, ARRAY_LENGTH(checksum));

    ptr = unsafe_strcpy(ptr, end, CHECKSUM_SEPARATOR);
    ptr = unsafe_strcpy(ptr, end, checksum);

    if (ptr == end)
        return FAIL;

    *ptr = '\0';   // very important!  unsafe_strcpy does not add a null at the end of the string
    return ptr - tagblock_str;
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
    }

    return num_fields;
}