/* tagblock definitions */


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


struct TAGBLOCK_FIELD
{
    char key[2];
    const char* value;
};

extern const char* group_field_keys[3];

const char* lookup_long_key(const char *short_key);
const char* lookup_short_key(const char* long_key);
size_t lookup_group_field_key(const char* long_key);
void extract_custom_short_key(char* buffer, size_t buf_size, const char* long_key);
void init_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields);

int split_fields(char* tagblock_str, struct TAGBLOCK_FIELD* fields, int max_fields);
int join_fields(const struct TAGBLOCK_FIELD* fields, size_t num_fields, char* tagblock_str, size_t buf_size);
int merge_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields, size_t max_fields,
                  struct TAGBLOCK_FIELD* update_fields, size_t num_update_fields);

int encode_fields(PyObject* dict, struct TAGBLOCK_FIELD* fields, size_t max_fields, char* buffer, size_t buf_size);

int encode_tagblock(char * dest, PyObject *dict, size_t dest_buf_size);
PyObject * decode_tagblock(char * tagblock_str);


