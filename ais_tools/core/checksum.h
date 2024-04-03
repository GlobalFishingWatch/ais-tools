/* AIS Tools checksum functions */

int checksum(const char *s);
char* checksum_str(char * __restrict dst, const char* __restrict src, size_t dsize);
bool is_checksum_valid(char* s);