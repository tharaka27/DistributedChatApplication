from models.configuration import ServerConfiguration

class FileReader:

    def populate(self,File_name):
        config_f = open(File_name,"r")
        data = config_f.readlines()
        database = {}
        
        for d in data:
            info = d.split(":")
            id = info[0].strip()
            value = info[1].strip()
            database[id] = value
        
        config_object = ServerConfiguration(database["server_name"],database["address"],database["client_port"],database["coordinator_port"])

        return config_object
        
