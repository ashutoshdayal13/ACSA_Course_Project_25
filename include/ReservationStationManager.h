#include "cp_includes.h"
#include "FUType.h"
#include "ReservationStation.h"
#include "Config.h"
class ReservationStationManager{
public:
    ReservationStationManager(const Config&);
    optional<RSEntry*>allocate_for(const Instruction&,Tag dest_tag);
    void on_broadcast(Tag tag,ll value);
    vector<RSEntry*> get_ready_for(FUType ft);
    bool has_free_entry(FUType ft);
private:
    map<FUType,ReservationStation*>stations;
};