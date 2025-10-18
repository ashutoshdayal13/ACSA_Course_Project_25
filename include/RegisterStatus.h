#include"Tag.h"
#include"cp_includes.h"
class RegisterStatus{
public:
    RegisterStatus(int);
    optional<Tag>get_tag(int);
    void set_tag(int,Tag);
    void clear_tag_if_matches(int,Tag);
    bool is_ready(int);
private:
    vector<optional<Tag>>reg_to_tag;
};