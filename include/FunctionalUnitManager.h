#include"cp_includes.h"
#include "IFunctionalUnit.h"
#include "Config.h"
class FunctionalUnitManager{
private:
    vector<IFunctionalUnit*>units;
public:
    FunctionalUnitManager(const Config&);
    optional<IFunctionalUnit*>find_free_unit(FUType);
    void tick_all();
    vector<pair<Tag,ll>>collect_finished_results();
};