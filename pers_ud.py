import re
import csv
import json
from bs4 import BeautifulSoup


def jsondata(file):
    f = open(file, 'r', encoding = 'utf-8')
    d = {}
    for line in f:
        if ':' in line:
            line = line.strip()
            line = line.split(':')
            d[line[0]] = line[1]
    f.close()
    return(d)

def features(postag):
    features = []
    if len(postag) < 1:
        return('')
    if postag[1] != '-':
        person = str(postag[1])
        features.append('Person=' + person)
    if postag[2] != '-':
        if postag[2] == 's':
            number = 'Sing'
        elif postag[2] == 'd':
            number = 'Plur'
        else:
            number = 'Dual'
        features.append('Number=' + number)
    if postag[3] != '-':
        if postag[3] == 'p':
            tense = 'Pres'
            aspect = 'Imp'
            features.append('Aspect=' + aspect)
        elif postag[3] == 'a':
            tense = 'Aor'
            aspect = 'Perf'
            features.append('Aspect=' + aspect)
        elif postag[3] == 'i':
            tense = 'Past'
            aspect = 'Imp'
            features.append('Aspect=' + aspect)
        elif postag[3] == 'r':
            tense = 'Past'
            aspect = 'Perf'
            features.append('Aspect=' + aspect)
        elif postag[3] == 'l':
            tense = 'Pqp'
        elif postag[3] == 'f':
            tense = 'Fut'
        elif postag[3] == 't':
            tense = 'Fut'
            aspect = 'Perf'
            features.append('Aspect=' + aspect)
        features.append('Tense=' + tense)
    if postag[4] != '-':
        if postag[4] == 'n':
            vform = 'Inf'
        elif postag[4] == 'p':
            vform = 'Part'
        else:
            vform = 'Fin'
            if postag[4] == 'i':
                mood = 'Ind'
            elif postag[4] == 'o':
                mood = 'Opt'
            elif postag[4] == 'm':
                mood = 'Imp'
            elif postag[4] == 's':
                mood = 'Sub'
            else:
                mood = 'EMPTY'
            features.append('Mood=' + mood)
        features.append('VerbForm=' + vform)
    if postag[5] != '-':
        if postag[5] == 'm':    
            voice = 'Mid'
        elif postag[5] == 'e':
            voice = 'Mid,Pass'
        elif postag[5] == 'p':
            voice = 'Pass'
        else:
            voice = 'Act' 
        features.append('Voice=' + voice)
    if postag[6] != '-':
        if postag[6] == 'm':
            gender = 'Masc'
        elif postag[6] == 'f':
            gender = 'Fem'
        else:
            gender = 'Neut'
        features.append('Gender=' + gender)
    if postag[7] != '-':
        if postag[7] == 'n':
            case = 'Nom'
        elif postag[7] == 'g':
            case = 'Gen'
        elif postag[7] == 'd':
            case = 'Dat'
        elif postag[7] == 'a':
            case = 'Acc' 
        else:
            case = 'Voc'
        features.append('Case=' + case)
    elif postag[8] != '-':
        if postag[8] == 'c':
            degree = 'Cmp'
        else:
            degree = 'Sup'
        features.append('Degree=' + degree)
    return('|'.join( features ))
    
def switch_heads(sent, id, head, head_rel, relation, rel, deppos, head_pos, head_head):
    if head_pos[0] == 'r' or (head_rel == 'COORD' and relation != 'conj' and relation != 'cop') or re.search('ad?v?cl', relation) != None:
        h = head_head
#        while head_rel == 'COORD':
#            new = sent.find_all(id=h)
#            for a in new:
#                a.get('head')
#                break
    elif relation == 'case' or relation == 'cc':
        if len(deppos) > 0:
            h = deppos[0]["id"]
        try: return(h)
        except: return(head)
    else:   
        h = head
    return(h)
    
p = json.dumps(jsondata('pos1.txt'))
pos1 = json.loads(p)
persfile = open('testfile.xml', 'r', encoding = 'utf-8')
soup = BeautifulSoup(persfile, 'lxml')
with open('output.conllu', 'w', newline='', encoding = 'utf-8') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t')
    cnt_sent = 1
    for se in soup.find_all("sentence"):
        for w in se.find_all("word"):
            id = w.get("id")
            form = w.get("form")
            lemma = w.get("lemma")
            if w.get("postag") == None:
                PoSP = '---------'
                pos = ''
                feat_list = ''
            else:
                if len(w.get("postag")) < 1:
                    PoSP = '---------'
                else:
                    PoSP = pos1[w.get("postag")[0]]
                pos = w.get("postag")
                feat_list = features(pos)
            head = w.get("head")
            c = se.find_all(id=head)
            rel = w.get("relation")
            if len(c) > 0: 
                i = c[0]
                head_lemma = i.get("lemma")
                head_pos = i.get("postag")
                head_rel = i.get("relation")
                head_head = i.get("head")
            dep = se.find_all(head = id)
            if head_pos == None:
                relation = ''
            deprels = []
            deppos = []
            if len(dep) > 0:
                for o in dep:
                    deprels.append(o.get("relation"))
                    deppos.append({'id':o.get("id"), 'head':o.get("head"), 'pos':o.get("postag"), 'rel':o.get("relation")})
            if lemma == 'εἰμί' and ('PNOM' in deprels or 'PNOM_CO' in deprels or 'COORD' in deprels):
                if 'COORD' in deprels:
                    for i in se.find_all(relation = 'COORD', head = id):
                        for j in se.find_all(head=i.get('id')):
                            if 'PNOM' in j.get('relation'):
                                relation = 'cop'
                                head = j.get('id')
                                break
                else:
                    relation = 'cop'
                    prnoms = se.find_all(relation = 'PNOM', head = id)
                    prnomsco = se.find_all(relation = 'PNOM_CO', head = id)
                    for i in prnoms:
                        head = i.get("id")
                        break

            elif 'SBJ' in rel:
                relation = 'subj'
                if pos[0] != 'v' or pos[4] == 'p':
                    relation = 'nsubj'
                else:
                    relation = 'csubj'
                if head_pos[5] == 'p':
                    relation = relation + 'pass'
            elif 'PRED' in rel:
                relation = 'root'
                head = '0'
            elif re.search('A[Tt][vV]+', rel) != None:
                relation = 'advmod' 
            elif 'ADV' in rel:
                if pos[0] == 'd' or re.search('[pn]', pos[4]) != None or pos[0] == 'g':
                    relation = 'advmod'
                elif head_rel == 'AuxP' or re.search('[dga]', pos[7]) != None:
                    relation = 'nmod'
                elif head_rel == 'AuxC':
                    relation = 'advcl'
                elif PoSP == 'ADP':
                    relation = 'case'
                else:
                    relation = 'ttt'
            elif rel == 'AuxP':
                relation = 'case'
            elif 'OCOMP' in rel:
                relation = 'xcomp'
            elif 'ATR' in rel:
                if 'SBJ' in deprels or 'SBJ_CO' in deprels:
                    relation = 'acl'
                else:
                    if re.search('[pn]', pos[0]) != None:
                        relation = 'nmod'
                    elif pos[0] == 'a' or (pos[0] == 'p' and pos[7] == head_pos[7]) or pos[4] == 'p':
                        relation = 'amod'
                    elif pos[0] == 'm':
                        relation = 'nummod'
                    elif pos[0] == 'l':
                        relation = 'det'
                    elif pos[0] == 'v' and re.search('[pn]', pos[4]) == None:
                        relation = 'acl'
                    elif (pos[0] == 'd' or pos[0] == 'g') and re.search('[vgd]', head_pos[0]) != None:
                        relation = 'advmod'
                    elif head_pos[0] == 'n':
                        relation = 'amod'
                    elif PoSP == 'ADP':
                        relation = 'case'
                    else:
                        relation = 'aaa'
            elif 'OBJ' in rel:
                if 'SBJ' in deprels or 'SBJ_CO'  in deprels or (pos[0] == 'v' and re.search('[pn]', pos[4]) == None):
                    relation = 'ccomp'
                elif pos[0] == 'v' or pos[7] == 'n':
                    relation = 'xcomp'
                elif pos[7] == 'a':
                    relation = 'dobj'
                elif re.search('[dg]', pos[7]) != None:
                    relation = 'iobj' 
                elif re.search('[dg]', pos[0]) != None:
                    relation = 'advmod'
                elif PoSP == 'ADP':
                    relation = 'case'
                else:
                    relation = 'ooo'
            elif rel == 'AuxC':
                relation = 'mark'
                PoSP = 'SCONJ'
                for i in se.find_all(id = head):
                    if 'ATR' in i.get('relation')  or 'ADV' in i.get('relation'):
                        head = i.get('id')
                        break
                    elif 'COORD' in i.get('relation'):
                        for j in se.find_all(head = i.get('id')):
                            head = j.get('id')
                            break
               
            elif rel == 'AuxY':
                relation = 'advmod'
            elif rel == 'AuxV':
                relation = 'aux'
            elif rel == 'AuxZ':
                if lemma == 'οὐ' or lemma == 'μή':
                    relation = 'neg'
                else:
                    relation = 'advmod'
            elif 'APOS' in rel:
                relation = 'appos'
            elif 'MWE' in rel:
                relation = 'mwe'
            elif PoSP == 'PUNCT':
                relation = 'punct'
                if head == '0':
                    head = str(int(id) - 1)
            elif PoSP == 'CONJ' or rel == 'COORD':
                relation = 'cc'
                PoSP = 'CONJ'
            elif ((pos[0] == 'd' or pos[0] == 'g') and re.search('[vgd]', head_pos[0]) != None):
                relation = 'advmod'
            else:
                relation = 'kkk'
            if 'PNOM' in rel:
                if 'PRED' in head_rel:
                    relation = 'root'
                    head = '0'
                else:
                    head = head_head
                    if 'ADV' in head_rel or 'AtvV' in head_rel:
                        relation = 'advmod'
                    elif 'ATR' in head_rel:
                        relation = 'amod'
                    elif 'OBJ' in head_rel:
                        relation = 'xcomp'
                    elif 'SBJ' in head_rel:
                        relation = 'nmod'
                    elif 'COORD' in head_rel:
                        for i in se.find_all(id = head_head):
                            if 'PRED' in i.get('relation'):
                                relation = 'root'
                            elif 'SBJ' in i.get('relation'):
                                relation = 'csubj'
                                for j in se.find_all(id=i.get('head')):
                                    if j.get('postag')[5] == 'p':
                                        relation = relation + 'pass'
                    else:
                        relation = 'koko'
            if '_CO' in rel and len(se.find_all(relation = rel[:-3] + '_CO')) > 1:
                if head_rel == 'COORD':
                    if lemma == se.find_all(relation = rel[:-3] + '_CO')[0].get('lemma'):
                        mainconj = id
                        head = head_head
                    else:
                        relation = 'conj' 
                        head = mainconj
            if rel != 'PNOM' and head_lemma == 'εἰμί':
                if len(se.find_all(relation='PNOM')) > 0:
                    for i in se.find_all(relation='PNOM'):
                        head = i.get("id")
                        break
            head = switch_heads(se, id, head, head_rel, relation, rel, deppos, head_pos, head_head)
            csvwriter.writerow([id] + [form] + [lemma] + [PoSP] + [pos] + [feat_list] + [head] + [relation] +['_'] + ['_'])
        cnt_sent += 1 
        csvfile.write('\n')
            
persfile.close()



        
        