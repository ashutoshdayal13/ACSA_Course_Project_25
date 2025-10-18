#include "cp_includes.h"
#include "RSEntry.h"
#include "IListener.h"
class ReservationStation:public Printable, public IListener{
private:
    vector<RSEntry>entries;
    string name;
public:
    ReservationStation(string,int);
    optional<RSEntry*>allocate(const Instruction&,Tag);

    void on_broadcast(Tag,ll) override;
    Tag get_listening_tag() const override;

    vector<RSEntry*>get_ready_entries();
    bool has_free_entry();
    string to_string() const override;
};