from models.configuration import ServerConfiguration

class FileReader:

    def populate(self,File_name):

        # read data from configuration file
        config_f = open(File_name,"r")
        data = config_f.readlines()
        config_f.close()

        servers = []

        for server_data in data:
            d = server_data.strip().split()
            servers.append(d)
        
        # create server configuration objects

        server_config_objs = []

        for each in servers:

            obj = ServerConfiguration(each[0],each[1],each[2],each[3], "666" + each[2][3], int(each[4]))
            server_config_objs.append(obj)

        return server_config_objs

        
