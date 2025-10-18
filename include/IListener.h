#include "cp_includes.h"
#include "Tag.h"
class IListener{
public:
    virtual ~IListener()=default;
    virtual void on_broadcast(const Tag&,ll)=0;
    virtual Tag get_listening_tag() const {
        return Tag::invalid();
    };
};