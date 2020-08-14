import pandas as pd
import numpy as np
import os

def txt2df(path):
    data = []
    index = []
    with open(path,'r',encoding="utf-8") as f:
        header = f.readline().strip().split('\t')
        while True:
            value = f.readline().strip().split('\t')
            if len(value)!=1:
                index.append(value[0])
                data.append(value[1:])
            else:
                break
    f.close()
    return np.array(data),index,header

def get_txts(path):
    return os.listdir(path)

def get_res(txtpath):
    df = pd.read_csv(txtpath,header=None,sep='\t').drop(columns=0).T
    df["label"] = txtpath.split('_')[-2]
    df.index = df["label"]
    df = df.drop("label",axis=1)
    return df

def aal():
    # ------------------aal--------------------
    aal_path = r"../combine/aal"
    list_aal = ["CSM116", "hc116"]

    aal_txt = os.path.join(aal_path, "aalutf8.txt")
    data, index, header = txt2df(aal_txt)

    for i in range(0, 116 - 1):
        for j in range(i + 1, 116):
            header.append(str(i + 1) + "_" + str(j + 1))

    dfaal = pd.DataFrame(data, index=index)
    dfaal.index = index

    df_ = pd.DataFrame()
    for a in list_aal:
        apath = os.path.join(aal_path, a)
        print(get_txts(apath))
        for txtpath in get_txts(apath):
            df = get_res(txtpath=os.path.join(apath, txtpath))
            df_ = pd.concat([df_, df], axis=0)
    df_.index = index

    df = pd.merge(dfaal, df_, left_index=True, right_index=True)
    df.to_csv(os.path.join(aal_path, "aalutf8.csv"), header=header)

def power():
    # ------------------power--------------------
    aal_path = r"../combine/power"
    list_aal = ["csm264", "hc264"]

    aal_txt = os.path.join(aal_path,"power264utf8.txt")
    data,index,header = txt2df(aal_txt)

    for i in range(0, 264 - 1):
        for j in range(i + 1, 264):
            header.append(str(i + 1) + "_" + str(j + 1))


    dfaal = pd.DataFrame(data,index=index)
    dfaal.index = index

    df_ = pd.DataFrame()
    for a in list_aal:
        apath = os.path.join(aal_path,a)
        print(get_txts(apath))
        for txtpath in get_txts(apath):
            df = get_res(txtpath=os.path.join(apath,txtpath))
            df_ = pd.concat([df_,df],axis=0)
    df_.index = index

    df = pd.merge(dfaal,df_,left_index=True,right_index=True)
    df.to_csv(os.path.join(aal_path,"power264utf8.csv"),header=header)

if __name__ == "__main__":
    power()
    pass