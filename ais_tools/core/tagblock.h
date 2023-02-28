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


/* tagblock_fields */

struct TAGBLOCK_FIELD
{
    char key[2];
    const char* value;
};

extern const char* group_field_keys[3];

const char* lookup_long_key(const char *short_key);
const char* lookup_short_key(const char* long_key);
int lookup_group_field_key(const char* long_key);
void extract_custom_short_key(char* buffer, size_t buf_size, const char* long_key);
void init_fields(struct TAGBLOCK_FIELD* fields, size_t num_fields);

int split_fields(struct TAGBLOCK_FIELD* fields, char* tagblock_str, int max_fields);
int join_fields(char* tagblock_str, size_t buf_size, const struct TAGBLOCK_FIELD* fields, size_t num_fields);
int merge_fields( struct TAGBLOCK_FIELD* fields, size_t num_fields, size_t max_fields,
                  struct TAGBLOCK_FIELD* update_fields, size_t num_update_fields);

/* tagblock_join */
int join_tagblock(char* buffer, size_t buf_size, const char* tagblock_str, const char* nmea_str);

/* tagblock_split */
int split_tagblock(char* message, const char** tagblock, const char** nmea);

/* tagblock_encode */
int encode_fields(struct TAGBLOCK_FIELD* fields, size_t max_fields, PyObject* dict, char* buffer, size_t buf_size);
int encode_tagblock(char * dest, PyObject *dict, size_t dest_buf_size);

/* tagblock_decode */
PyObject * decode_tagblock(char * tagblock_str);

/* tagblock_update */
int update_tagblock(char * dest, size_t dest_size, char* message, PyObject * dict);

