import numpy as np
import datetime
import plotly.express as px
import pandas as pd
import streamlit as st

df = pd.read_csv('data.csv', index_col=0)
df = df.replace({'NN':'N', 'NO':'N', 'NX':'N'})
color_class = {'A':'red', 'B':'blue', 'C1':'lightgreen', 'C2':'limegreen', 'N':'yellow', 'NL':'pink'}
color_man = {'Honda':'red', 'Suzuki':'yellow', 'Kawasaki':'limegreen', 'Yamaha':'blue', 'KTM':'orange', 'Ducati':'crimson'}
list_man = df['Manufacturer'].unique()

st.title('MotoGymkhana Result Database')
st.text('出典: 二輪ジムカーナ主催者団体協議会（ＪＡＧＥ） http://jage.jpn.org/claro/index.html')
st.text('データはJAGE HP記載の2011年以降のDUNLOP杯、JAGE杯のリザルトを加工し作成')


st.title('【シーズン別出走車両台数推移】')
st.text('注記）のべエントリー数で集計')

df_entry = df.groupby(['Season', 'Manufacturer'], as_index=False).count()
df_entry = df_entry[['Season','Manufacturer', 'Rider']]

fig = px.bar(
    data_frame = df_entry.sort_values('Rider', ascending=False),
    x = 'Season',
    y = 'Rider',
    color = 'Manufacturer',
    color_discrete_map = color_man,
    labels = {'Rider':'のべ出走台数（台）'},
)
st.plotly_chart(fig)

df_season = pd.crosstab(df.Season, df.Manufacturer, margins=True).sort_values(by='All', axis=1, ascending=False).iloc[:-1, 1:]
df_season



st.title('クラス昇格者の使用車両')
classup_list = ['Bへ昇格', 'C1へ昇格', 'C2へ昇格']
option_classup = st.selectbox('選択して下さい', classup_list)

#B級昇格者の抽出
to_b = df[df['Rating[%]'] < 105]
to_b = to_b[(to_b['Class'] !='A') & (to_b['Class']!= 'B')]

#C1級昇格者の抽出
to_c1 = df[df['Rating[%]'] < 110]
to_c1 = to_c1[(to_c1['Class'] !='A') & (to_c1['Class']!= 'B') & (to_c1['Class']!= 'C1')]

#C2級昇格者の抽出
to_c2 = df[df['Rating[%]'] < 115]
to_c2 = to_c2[to_c2['Class'].str.contains('N')]

if option_classup == 'Bへ昇格':
    df_classup = to_b
elif option_classup == 'C1へ昇格':
    df_classup = to_c1
else:
    df_classup = to_c2

slider_range = st.slider(
    '抽出期間を選択',
    value = [2011, 2021],
    min_value = 2011,
    max_value = 2021,
    step = 1
    )

df_classup = df_classup[(df_classup['Season']>=slider_range[0])&(df_classup['Season']<=slider_range[1])]
temp = df_classup.groupby(['Machine', 'Manufacturer'], as_index=False).count()[['Machine','Rider', 'Manufacturer']].sort_values('Rider', ascending=False)
df_classup = df_classup['Machine'].value_counts()

fig = px.bar(
    df_classup.sort_values().reset_index().rename(columns={'index': 'Machine', 'Machine':'昇格者数（人）'}),
    x = '昇格者数（人）',
    y = 'Machine',
    orientation = 'h'
)
st.plotly_chart(fig)
temp



st.title('【車両別データ】')
option_man = st.selectbox('メーカーを選択', np.sort(list_man), index=4)
machine_list = df[df['Manufacturer']==option_man]['Machine'].unique()
option_machine = st.selectbox('車両を選択', np.sort(machine_list), index=10)
df_machine = df[df['Machine']==option_machine]
ex_dup = st.checkbox('シーズン中の同一ライダーの重複を除く')

if ex_dup == True:
    temp = pd.DataFrame()
    for year in df_machine['Season'].unique():
        df_year = df_machine[df_machine['Season']==year].sort_values('Class')
        all_machine = df_year[~df_year['Rider'].duplicated()]
        temp = pd.concat([temp, all_machine])
    df_machine = temp

#df_machine

st.header('出走台数推移')

year_max = df['Season'].max() + 1
year_min = df['Season'].min() - 1

fig = px.bar(
    data_frame = df_machine.groupby(['Season', 'Class'], as_index=False).count()[['Season', 'Class', 'Rider']].sort_values('Class'),
    x = 'Season',
    y = 'Rider',
    range_x = [year_min, year_max],
    color = 'Class',
    color_discrete_map = color_class,
    labels = {'Rider':'出走台数（台）'},
)
st.plotly_chart(fig)



st.header('タイム比推移・分布')
class_list = ['全て', 'A', 'B', 'C1', 'C2', 'N', 'NL']
option_class = st.selectbox('クラスを選択', class_list)
if option_class == '全て':
    df_class = df
else:
    df_class = df[df['Class']==option_class]
df_class = df_class[df_class['Machine']==option_machine]

fig = px.scatter(
    data_frame = df_class.sort_values('Class'),
    x = 'Date',
    y = 'Rating[%]',
    color = 'Class',
    color_discrete_map = color_class,
    range_x = [datetime.datetime(2011,1,1), datetime.datetime.now()],
    range_y = [df_class['Rating[%]'].max(), 100],
    labels = {'Rating[%]':'タイム比[%]'}
)
st.plotly_chart(fig)

# df_class_min = pd.DataFrame(df_class.groupby('Date')['Rating[%]'].min()).rename(columns={'Rating[%]':'Top'})
# df_class_ave = pd.DataFrame(df_class.groupby('Date')['Rating[%]'].mean()).rename(columns={'Rating[%]':'Average'})
# df_class_max = pd.DataFrame(df_class.groupby('Date')['Rating[%]'].max()).rename(columns={'Rating[%]':'Worst'})
# df_class = pd.concat([df_class_min, df_class_ave, df_class_max], axis=1)

# #df_class
# df_class = df_class.reset_index()

# fig = px.line(
#     data_frame = df_class,
#     x = 'Date',
#     y = ['Top', 'Average', 'Worst'],
#     range_x = [datetime.datetime(2011,1,1), datetime.datetime.now()],
#     range_y = [df_class['Worst'].max(), 100],
#     labels = {'value':'タイム比[%]'}
# )
# st.plotly_chart(fig)

slider_range2 = st.slider(
    '期間を選択',
    value = [2011, 2021],
    min_value = 2011,
    max_value = 2021,
    step = 1
    )

fig = px.histogram(
    data_frame = df_class[(df_class['Season']>=slider_range2[0]) & (df_class['Season']<=slider_range2[1])].sort_values('Class'),
    x = 'Rating[%]',
    color = 'Class',
    range_x = [100, 160],
    barmode = 'stack',
    color_discrete_map = color_class,
)

st.plotly_chart(fig)