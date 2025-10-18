#include"Tag.h"

atomic<ull> Tag::nxt_id_{1};

Tag::Tag():id(-1){}
Tag::Tag(ull id_):id(id_){}

Tag Tag::next_tag(){
    return Tag(nxt_id_.fetch_add(1));
}
Tag Tag::invalid(){
    return Tag(-1);
}

bool Tag::operator==(const Tag&o) const { return id==o.id; }
bool Tag::operator<(const Tag&o) const {return id<o.id; }

ull Tag::get_id() const { return id; }

string Tag::to_string()const {
    if(id==-1)return "T<invalid>";
    return "T"+std::to_string(id);
}