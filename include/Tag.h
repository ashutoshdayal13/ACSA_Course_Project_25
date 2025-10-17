#include "cp_includes.h"
#include "Printable.h"
class Tag:public Printable{
public:
    static Tag next_tag();
    static Tag invalid();

    bool operator==(const Tag&) const;
    bool operator<(const Tag&) const;
    lid get_id();
    string to_string() const override;
private:
    lid id;
    static atomic<ll> nxt_id_;
    Tag()=default;
    Tag(lid id_);
};