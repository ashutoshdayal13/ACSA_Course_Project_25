#include "cp_includes.h"
#include "IListener.h"
using Arbiter=function<int(vector<pair<Tag,ll>>)>;

class CDB{ //Singleton 
private:
    CDB()=default;
    CDB(const CDB&)=delete; 
    CDB& operator=(const CDB&)=delete;
    static CDB *ptr;

    set<IListener*>listeners;

public:
    static CDB* get_instance();
    ~CDB();
    Arbiter arbiter;

    void subscribe(IListener*);
    void unsubscribe(IListener*);
    void broadcast(Tag,ll);
    void broadcastMultiple(vector<pair<Tag,ll>>);
};