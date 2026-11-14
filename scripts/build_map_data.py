"""Build the compact JSON that prototype/pulso-mibici.html embeds, from data/raw/datos_abiertos_*.csv and nomenclatura_*.csv (October 2026).
Aggregates only: per-station totals and hourly counts, the top 600 origin-destination pairs, and a 6,000-trip sample of one weekday."""
import pandas as pd, numpy as np, json, re, sys
import pathlib; D=str(pathlib.Path(__file__).resolve().parent.parent/'data'/'raw')+'/'
t=pd.read_csv(D+'datos_abiertos_2026_10.csv',dtype=str)
t.columns=['trip','user','gender','birth','start','end','o','d']
n0=len(t)
t['start']=pd.to_datetime(t.start,errors='coerce'); t['end']=pd.to_datetime(t.end,errors='coerce')
t['o']=pd.to_numeric(t.o,errors='coerce'); t['d']=pd.to_numeric(t.d,errors='coerce')
t['min']=(t.end-t.start).dt.total_seconds()/60
ok=t.start.notna()&t.end.notna()&t.o.notna()&t.d.notna()&t['min'].between(1,1440)
t=t[ok].copy(); t[['o','d']]=t[['o','d']].astype(int)
s=pd.read_csv(D+'nomenclatura_2026_10.csv',encoding='latin-1')
s.columns=['id','name','lat','lon','cap']
def clean(n):
    m=re.match(r'\((\w+)-(\d+)\)\s*(.*)',str(n)); 
    return (m.group(1),m.group(1)+'-'+m.group(2),re.sub(r'\s+',' ',m.group(3)).strip()) if m else ('',  '', str(n))
s[['muni','code','label']]=s.name.apply(lambda n: pd.Series(clean(n)))
t['h']=t.start.dt.hour; t['dow']=t.start.dt.dayofweek
dep=t.groupby('o').size(); arr=t.groupby('d').size()
s['dep']=s.id.map(dep).fillna(0).astype(int); s['arr']=s.id.map(arr).fillna(0).astype(int)
unknown=sorted(set(t.o)|set(t.d)-set(s.id)); 
hd=t.groupby(['o','h']).size().unstack(fill_value=0).reindex(columns=range(24),fill_value=0)
ha=t.groupby(['d','h']).size().unstack(fill_value=0).reindex(columns=range(24),fill_value=0)
s=s[(s.dep+s.arr)>0].copy()
days=t.start.dt.date.nunique()
wk=t[t.dow<5]; we=t[t.dow>=5]
st=[]
for r in s.itertuples():
    st.append({'id':int(r.id),'c':r.code,'m':r.muni,'n':r.label,'lat':round(r.lat,6),'lon':round(r.lon,6),'cap':int(r.cap),'dep':int(r.dep),'arr':int(r.arr),
      'hd':[int(x) for x in (hd.loc[r.id] if r.id in hd.index else [0]*24)],'ha':[int(x) for x in (ha.loc[r.id] if r.id in ha.index else [0]*24)]})
od=t[t.o!=t.d].groupby(['o','d']).size().sort_values(ascending=False)
valid=set(s.id); od=od[[ (a in valid and b in valid) for a,b in od.index]].head(600)
flows=[[int(a),int(b),int(c)] for (a,b),c in od.items()]
# sample one representative weekday for trip animation
day=wk.start.dt.date.value_counts().index[0]
dd=t[(t.start.dt.date==day)&t.o.isin(valid)&t.d.isin(valid)&(t.o!=t.d)]
samp=dd.sample(min(6000,len(dd)),random_state=14)
trips=[[int(r.o),int(r.d),int((r.start-pd.Timestamp(day)).total_seconds()//60),int(round(r.min))] for r in samp.itertuples()]
hr_all=t.groupby('h').size().reindex(range(24),fill_value=0)
hr_wk=(wk.groupby('h').size().reindex(range(24),fill_value=0)/wk.start.dt.date.nunique()).round(1)
hr_we=(we.groupby('h').size().reindex(range(24),fill_value=0)/max(1,we.start.dt.date.nunique())).round(1)
age=2026-pd.to_numeric(t.birth,errors='coerce')
k={'rows_in':n0,'trips':int(len(t)),'dropped':int(n0-len(t)),'days':int(days),'from':str(t.start.min().date()),'to':str(t.start.max().date()),
 'per_day':round(len(t)/days),'median_min':round(float(t['min'].median()),1),'stations':len(st),'users':int(t.user.nunique()),
 'peak_hour':int(hr_all.idxmax()),'anim_day':str(day),'anim_day_trips':int(len(dd)),'sampled':len(trips),
 'female_pct':round(100*float((t.gender=='F').mean()),1),'age_median':float(age[(age>12)&(age<90)].median()),
 'hr_wk':[float(x) for x in hr_wk],'hr_we':[float(x) for x in hr_we],
 'munis':s.groupby('muni').size().to_dict()}
json.dump({'k':k,'st':st,'flows':flows,'trips':trips},open(pathlib.Path(__file__).resolve().parent/'map_data.json','w'),separators=(',',':'),ensure_ascii=False)
print(json.dumps(k,ensure_ascii=False)[:900]); import os; print('json bytes',os.path.getsize('data.json'))
top=s.assign(net=s.arr-s.dep).sort_values('net'); print(top[['code','label','dep','arr','net']].head(4).to_string()); print(top[['code','label','dep','arr','net']].tail(4).to_string())
