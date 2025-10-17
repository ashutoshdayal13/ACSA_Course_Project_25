#include "cp_includes.h"
#include "RSEntry.h"
class ReservationStation:public Printable{
private:
    vector<RSEntry>entries;
    string name;
public:
    ReservationStation(string name,int size);
    optional<RSEntry*>allocate(const Instruction&,Tag);
    void on_broadcast(Tag,ll);
    vector<RSEntry*>get_ready_entries();
    bool has_free_entry();
    string to_string() const override;
};