#include "cp_includes.h"
#include "RSEntry.h"
#include "FUType.h"
class IFunctionalUnit{
public:
    virtual bool assign(RSEntry*);
    virtual void step();
    virtual bool is_free();
    virtual optional<pair<Tag,ll>> fetch_results_if_ready();
    virtual FUType get_type();
};