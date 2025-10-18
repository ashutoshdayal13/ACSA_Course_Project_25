#include"cp_includes.h"
#include"RSEntry.h"
#include"Instruction.h"
class LoadBuffer{
public:
    optional<RSEntry*>allocate_load(const Instruction&);
    void on_broadcast(Tag,ll);
    vector<RSEntry*>get_ready_loads();
private:
    vector<RSEntry>entries;
};