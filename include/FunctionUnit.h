#include "FUType.h"
#include "RSEntry.h"
#include "cp_includes.h"
#include "IFunctionalUnit.h"
class FunctionalUnit:public IFunctionalUnit, public Printable{
public:
    FunctionalUnit(FUType,int);
    bool assign(RSEntry*) override;
    void step() override;
    bool is_free() override;
    optional<pair<Tag,ll>>fetch_results_if_ready() override;

    string to_string() const override;
private:
    FUType type;
    int latency;
    RSEntry* current_entry;
    int cycles_left;
};