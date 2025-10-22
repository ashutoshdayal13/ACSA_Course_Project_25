#include "cp_includes.h"
#include "Printable.h"
class Tag:public Printable{
public:
    static Tag next_tag();
    static Tag invalid();

    bool operator==(const Tag&) const;
    bool operator<(const Tag&) const;
    ull get_id() const;
    string to_string() const override;
private:
    ull id;
    static atomic<ull> nxt_id_;
    Tag();
    Tag(ull id_);
};