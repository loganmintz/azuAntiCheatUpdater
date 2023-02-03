import requests, zipfile, json, io, re, os
from json import JSONEncoder

class mod:
    def __init__(self, namespace, name, version, whitelist=0, nochange=0):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.whitelist=whitelist
        self.nochange = nochange
        
from json import JSONEncoder #JSON handling for the mod class
class modEncoder(JSONEncoder):
        def default(self, o):
            
            return o.__dict__


    
#global vars
thunderstore_api_url = "https://thunderstore.io/api/experimental/package/"
target_modpack_name = "TAG_Ocean_Exploration"
target_modpack_namespace = "Poor_Boy_Jab"

mod_whitelist = []
mod_greylist = []


#Queries the Thunderstore API and returns a array of mods. Docs here: https://thunderstore.io/api/docs/
def retrieve_raw_modlist(modpack_namespace, modpack_name):  
    modpack_url = thunderstore_api_url + modpack_namespace + "/" + modpack_name 
    print(f"Retrieving latest version of {modpack_name} from Thunderstore")
    try:
        response = requests.get(modpack_url).json()
    except:
        print(f"Could not find {modpack_namespace}/{modpack_name} at {modpack_url}")
    print(f"Successfully retrived {modpack_name} from Thunderstore")
 
    return response["latest"]["dependencies"]

#Takes in a dict of the API response from Thunderstore and returns an array of the mod
def refine_modlist(history, raw):
    mod_list = [] #this is the return
    i=0
    for modpack_mod in raw: #retrieve the neccessary infor about each mod
        part = modpack_mod.split("-")     #this works because the api enforces the rule of separting the namespace, name, and version with '-'
        if part[0] == "LVH":                #except for here, for what I assume are historical reasons. Either way this is a hack and needs to be changed.
            stupid_fix = part[0] + "-" + part[1]
            mod_list.append(mod(stupid_fix,part[2],part[3]))
        else:
            mod_list.append(mod(part[0],part[1],part[2]))
        try:
            for h_mod in history:
                if h_mod["namespace"] == mod_list[i].namespace and h_mod["name"] == mod_list[i].name:
                    mod_list[i].nochange = 1
        except:
            pass
        i+=1
    return mod_list

#takes in an array of mods and returns a whitelist and a greylist.
def define_whitelist(mod_list):
    for m in mod_list:
        if m.nochange == 0:
            inp=None
            inp = input(f"Add {m.name} {m.version} to the whitelist? (y/n): ")
            if inp == 'y':
                print("Adding", m.name, "to the whitelist")
                m.whitelist = 1
                mod_whitelist.append(m)
            else:
                print("Adding", m.name, "to the greylist")
                mod_greylist.append(m)
        else:
            if m.whitelist == 1:
                mod_whitelist.append(m)
            else:
                mod_greylist.append(m)
    return mod_whitelist, mod_greylist


#Extract the neccessary DLL's from Thunderstore and place them in clear subfolders
def download_and_unzip_dlls(mod_list, list_type):
    for m in mod_list:
        if m.name != "BepInExPack_Valheim" and m.name != "HookGenPatcher": #bit of a hack here, but these are common and never should be used here
            print(f"{m.namespace}-{m.name}-{m.version} in list: {list_type}, downloading")
            zip_file_url =  "https://cdn.thunderstore.io/live/repository/packages/" + m.namespace + "-" + m.name + "-" + m.version + ".zip"
            target_path = os.getcwd() + "\AzuAntiCheat_" + list_type
            r = requests.get(zip_file_url, stream=True)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            for info in z.infolist():
                if re.match(r'.*\.dll$', info.filename):
                    z.extract(info, path=target_path)
                    print(f"Extracted: {info.filename}")
            

#Write the list of mods added or changed to a JSON doc to speed up the next run
def write_list_to_file(mod_list):
    target_path = os.getcwd() + "\AzuAntiCheatModList.json"
    # Serializing json
    json_object = json.dumps(mod_list, cls=modEncoder)
    
    # Writing to sample.json
    with open(target_path, "w") as outfile:
        outfile.write(json_object)


#Gets the history and returns as a dict
def read_mod_history():
    target_path = os.getcwd() + '\AzuAntiCheatModList.json'
    try:
        with open(target_path) as historical_file:
            file_contents = historical_file.read()
        return json.loads(file_contents)
    except:
        print(f"No history found, proceeding...")
        pass


#main program
historic_mod_list = read_mod_history()
raw_mod_list = retrieve_raw_modlist(target_modpack_namespace, target_modpack_name)

mod_list = refine_modlist(historic_mod_list, raw_mod_list)
whitelist, greylist = define_whitelist(mod_list)

#record and dump to list
download_and_unzip_dlls(whitelist, "Whitelist")
download_and_unzip_dlls(greylist, "Greylist")

write_list_to_file(mod_list)
