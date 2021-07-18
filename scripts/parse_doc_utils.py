import re
import io
import os
import numpy as np

def _get_sta_of_demos(text):
    return([m.start() for m in re.finditer('Demo',text)])

def _get_object_names(text):
    pattern = r'''(Objects:) ((\w+))'''
    return([b for id, a, b in re.findall(pattern,text,re.MULTILINE)])


def _add_missing_objects_id(text,start_of_line,repl):
    """
    Identifies lines in which objects were summarised within one message. Presumably because they were in the same frame.
    It adds text to the beginning of the lines.
    It is recursively so that the indeces are updated for each change in the text.
    We are not interested in words within the header so I set a arbitrary threshold at 500. This could be reworked.
    """
    sta_obj = [m.start() for m in re.finditer('(\\n\w+)',text) if text[m.start():m.start()+len(start_of_line)] != start_of_line]
    sta_obj = [x for x in sta_obj if x >500]
    
    if len(sta_obj)==0:
        return(text)
    
    text = text[:sta_obj[0]] + repl + text[sta_obj[0]+1:]
    
    return(_add_missing_objects_id(text,start_of_line,repl))

def _add_whitespace(pattern,repl,text):
    text = re.sub(pattern,repl,text)
    return(text)

def _check_length(*args):
    l = [len(x) for x in args]
    return(l)

def _split_text_in_demos(text):
    """
    Finds the keyword demo and splits the text if the keyword is repeated. The demos are
    then stored in a dictionary
    """
    sta_of_demo = _get_sta_of_demos(text)
    print(f"There were {len(sta_of_demo)} demos detected in the challenge text file.")
    print("-"*15)
    
    demos = {}
    len_sta_of_demo = len(sta_of_demo)
    for ind, val in enumerate(sta_of_demo):
        if ind+1 < len_sta_of_demo:
            demos['demo'+str(ind)]  =  text[sta_of_demo[ind]:sta_of_demo[ind+1]-1]
        else:
            demos['demo'+str(ind)]  =  text[sta_of_demo[ind]:]
    return(demos)


def _save_demos_after_split(demos_dir,demos_file_path,text,key):
    """
    This saves the demos as text files in the data/demo directory
    """
    dfp = os.path.join(demos_dir,key +'.txt')
    demos_file_path.append(dfp)
    text_file = open(dfp, "w")
    n = text_file.write(text)
    text_file.close()
    return(demos_file_path)


def _preprocess(text):
    """
    Some touch ups for the text so that it is human readable 
    """
    text = text.replace('\n\n',' ')
    text = re.sub('Objects:', 'Objects0:', count = 1,string=text)
    text = text.replace('\nObjects',' Objects')
    #text = _add_missing_objects_id(text,'\nFPS ','\nObjects: ')
    text = text.replace(') FPS:',') \nFPS:')
    text = _add_whitespace("FPS:","FPS: ",text)
    text = _add_missing_objects_id(text,'\nFPS','\nFPS: NULL 	 AVG_FPS: NULL Objects: ')  
    return(text)




def _split_and_preprocess(file_path):
    """
    Opens the yolo output text file and checks if multiple demos are within the file.
    If so the text file is split into multiple text files which are saved and stored in a dictionary.
    The demos are then preprocessed so that the text file is in human readable format.
    Output:
    
    demos_file_path:    list with file paths to saved demos
    original_demo1:     demo1 text before preprocessing
    preporcessed_demo1: demo1 text after preprocessing
    
    """
    file_object = open(file_path, 'r')
    text = file_object.read()
        
    demos = _split_text_in_demos(text)
    demos_dir = './data/demos/'
    if not os.path.exists(demos_dir):
        os.mkdir(demos_path)

    demos_file_path = []
    for key, val in demos.items():
        original_demo1 = demos[key]
        text = _preprocess(demos[key])
        preporcessed_demo1 = text
        
        demos_file_path = _save_demos_after_split(demos_dir,demos_file_path,text,key)
        
    print(f"The challenge text file was split into {len(demos_file_path)} separate text files.\nThe text files were renamed and saved under {demos_file_path}"  )
    print("-"*15)
    return(demos_file_path,original_demo1,preporcessed_demo1)


    

    