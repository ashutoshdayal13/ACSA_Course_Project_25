#include "cp_includes.h"
#include "Tag.h"
class IListener{
public:
    virtual void on_broadcast(Tag,ll);
    virtual Tag get_listening_tag() const;
};