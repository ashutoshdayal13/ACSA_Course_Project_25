class CDB{ //Singleton
public:
    static CDB* getInstance();
    ~CDB();
private:
    CDB()=default;
    CDB(const CDB&)=delete; 
    CDB& operator=(const CDB&)=delete;
    static CDB *ptr;
};