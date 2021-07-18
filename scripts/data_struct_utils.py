import re
import io
import os
import numpy as np
import warnings

def _get_accuracy(text):
    """
    Find index of % sign and step back to get accuracy
    """
    sta_obj = [m.start() for m in re.finditer('%',text)]
    return([float(text[x-3:x:1]) for x in sta_obj])

def _get_val_from_id(text,ID):
    """
    Searches ID in text using regular expressions. The search results are
    returned as list
    """
    pattern = rf'''({ID})\s+((\d+\.\d+|\w+\s+x\s+\d+|\d+|\w+))'''
    data = [b for id, a, b in re.findall(pattern,text,re.MULTILINE)]
    #print(ID)
    if ID in ["\nFPS:","AVG_FPS:"]:
        data =  [data[counter-1]if value =="NULL" else value for counter,value in enumerate(data)]
        
    if ID in ["\nFPS:","AVG_FPS:"]:
        data = [float(x) for x in data]
    elif ID in ["left_x:","top_y:","width:","height:","Accuracy"]:
        data = [int(x) for x in data]
    elif ID == "Video stream:" :
        data = [int(x)for x in data[0].replace("x","").split()]
    
    return(data)

def _build_data_struct(file_path,_type):
    """
    Builds a dictionary data keys ("Objects:","left_x:","top_y:","width:","height:","\nFPS:","AVG_FPS:","Video stream:","Accuracy").
    The values are read out via reguar expressions
    
    return: the data structure which was created and the text that was read out
    """
    file_object = open(file_path, 'r')
    text = file_object.read()
    data_names = ["Objects:","left_x:","top_y:","width:","height:","\nFPS:","AVG_FPS:","Video stream:","Accuracy"]
    
    
    if _type == "dict":
        data_struct = {}
        
        for n in data_names:
            
            if n == "Accuracy":
                data_struct[n]      = _get_accuracy(text)
            else:
                nk = n 
                nk = nk.replace(":","").replace("\n","")
                data_struct[nk] = _get_val_from_id(text,n)
                
        if all([len(data_struct[key]) for key in data_struct.keys()]):
            print("Keys have the same lengths")
        else:
            warnings.warn("Keys have different lengths!")

    return(data_struct,text)
 
    
    
def _get_number_of_unique_objects(data_struct):
    obj = list(set(data_struct["Objects"]))
    nr_of_obj = len(obj)
    return(nr_of_obj,obj)

def _get_number_of_object_detections(data_struct):
    nr_of_obj_det = len(data_struct["Objects"])
    return(nr_of_obj_det)


def _make_category_groups(data_struct):
    """
    OBSOLET DONT USE
    Creates a dictionary names groups with as many keys as unique objects in yolo output.
    
    """
    groups = {}
    for cat in set(data_struct["Objects"]):        
        
        data_names  = ["left_x","top_y","width","height","FPS","AVG_FPS","Accuracy"]
        indices     = [i for i, x in enumerate(data_struct["Objects"]) if x == cat]
        for dn in data_names:
            for idx in indices:
                groups[cat] = data_struct[dn][idx]
    return(groups)

def _split_into_categories(data_struct):
    """
    Creates a dictionary names groups with as many keys as unique objects in yolo output.
    The values are arrays which contain all numerical variables from the data_struct dictionary.
    This could be reworked by dummy encoding the string variables. This way we could remove the 
    data_struct completly.
    """
    data_names  = ["left_x","top_y","width","height","FPS","AVG_FPS","Accuracy"]
    groups = {}

    for cat in set(data_struct["Objects"]):        
        indices     = [i for i, x in enumerate(data_struct["Objects"]) if x == cat]
        mask = []
        mask = np.empty((len(indices),len(data_names)))

        for counter,value in enumerate(data_names):
            mask[:,counter]  = np.array(data_struct[value])[indices]

        groups[cat] = mask
    
    return(groups,data_names)


def _get_typical_position(data_struct):
    """
    Splits the data-struct into groups/categories. Creates a dictionary names groups with as many 
    keys as unique objects in yolo output.  
    Next we loops over the groups dictionary and calculate the means for 
        left_x, 
        top_y;
        width,
        height,
        right_x,
        bot_y,
    Output:
    groups:     dictionary with data as array
    mean_dictI: dictionary with mean data
    ident_dict: an encoding dictionary to identify the columns in groups[0:6] and mean_dict
    """
    
    # Split into groups
    groups,data_names        = _split_into_categories(data_struct)
    data_names.append('right_x')
    data_names.append('bot_y')
    ident_dict = {value:counter for (counter,value) in enumerate(data_names)}


    mean_dict = {} 

    for (counter,key) in enumerate(groups):

        cat = groups[key]

        left_x = cat[:,0]
        top_y  = cat[:,1]
        width  = cat[:,2]
        height = cat[:,3]

        right_x = left_x + width
        bot_y   = top_y + height 

        cat = np.append(cat, right_x[:, None], axis=1)
        cat = np.append(cat, bot_y[:, None], axis=1)

        mean_dict[key] = {'mean_'+key: cat[:,value].mean().round(2) for (key,value) in ident_dict.items()}

        
    return(groups,mean_dict,ident_dict)


def _get_means_for_print_output(mean_dict,key):

    top = (mean_dict[key]["mean_left_x"],mean_dict[key]["mean_top_y"])
    bot = (mean_dict[key]["mean_right_x"],mean_dict[key]["mean_bot_y"])
    w = mean_dict[key]["mean_width"]
    h = mean_dict[key]["mean_height"] 

    return(top,bot,w,h)