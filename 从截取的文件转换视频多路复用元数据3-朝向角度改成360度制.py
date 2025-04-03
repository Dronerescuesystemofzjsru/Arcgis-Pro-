import pandas as pd
from datetime import datetime, timedelta
import csv

def convert_dms_to_decimal(degrees, minutes, seconds):##这个函数：度分秒单位制转换成带小数的度数的单位制
    decimal_degrees = degrees + minutes/60 + seconds/3600
    return decimal_degrees

def get_record_by_seconds(record_df):
    record_by_seconds=[]
    record_per_sec=[]
    sec_dttm=-1
    j=0
    for i in range(len(record_df)):
        
        if i==0:
            sec_dttm=record_df.values[i][1]
        elif record_df.values[i][1]!=sec_dttm:##进入下一秒以后保存并打印上一秒的值，所以append不在前面写
            record_by_seconds.append(record_per_sec)
            print("第",j,"秒：",sec_dttm," 的记录条数为：",len(record_per_sec))
            record_per_sec=[]
            j+=1
            sec_dttm=record_df.values[i][1]##更新秒数

        elif i==len(record_df)-1:##此分支是为了处理最后一轮循环
            ##由于最后一行没有下一行了，所以直接检测是否到了最后一行，到了就把列表写入并打印##没有这一步会缺一秒
            record_per_sec.append(i)#因为没下一轮循环，提前保存，所以要在保存这一秒的数据前 提前把最后一个值写入record_per_sec
            record_by_seconds.append(record_per_sec)
            print("第",j,"秒：",sec_dttm," 的记录条数为：",len(record_per_sec))

            break##最后一次在存入record_by_seconds之前加，存入以后就不可以在本轮循环再加了。所以直接跳过最后一轮循环的最后一句话。

        record_per_sec.append(i)##先判断是否过了一个秒再添加。因为判断一秒是否结束的方法是是否进入了下一秒。
    return record_by_seconds

def make_timestamp(firstnum,record_df):
    timestamps=[]
    frame_time=pd.to_datetime(record_df.values[firstnum][1],utc=True)##第二秒的记录的精确开始时间，作为所有前面的时间和后面的时间的基准

    ##record_time  Timestamp('2024-06-17 09:22:27')
    rcd_time= pd.to_datetime(record_df.values[0][1], utc=True)##2025.2.21 移出循环以后，直接找第一条记录的时间，因为第一秒的记录的日志时间都一样
    print("第一条记录的记录时间：",rcd_time)

    for i in range(firstnum):
        
        ##用frame_time减去相差值
        minus_time=timedelta(seconds=(firstnum-i)*0.1)
        pre_frame_time=frame_time-minus_time##第一次循环中不用每次递加或递减的方法，也不改变frame_time的值
        #2025.2.21 例如，资料一的第一秒有两条记录，firstnum==2,故第一轮循环i==0然后秒数=（2-0）*0.1=0.2，
        #然后用frame_time减去0.2s即得出2024-06-17 09:23:49.800000 即为第一条记录的推测时间
        #同理，第二条记录中minus_time=（2-1）*0.1=0.1s,frame_time-0.1后剩下0.9s 故应该是09:23:49.900000，也即比frame_time少0.1s

        #2025.2.21 运行结果：


        print("第一秒中第",i,"条记录的推测时间：",pre_frame_time)

        timestamp=pre_frame_time.timestamp()##转换成时间戳####2025.2.21 使用基于第二秒为基准时间的推测时间，而不是第一秒的日志时间
        timestamp_16decimalplace=int(timestamp*1000000)#换成16位##原来是纳秒，如1.718616229e+18 1*10^18 是19位。于是16位就是微秒 #原来9个0现在6个
        timestamps.append(timestamp_16decimalplace)
        print("第一秒中第",i,"条记录的时间戳：",timestamp_16decimalplace)
    
    addtime=timedelta(seconds=0.1)##每次加0.1秒
    for i in range(firstnum,len(record_df)):
        print(frame_time)
        frame_time_stamp=frame_time.timestamp()
        timestamp_16decimalplace=int(frame_time_stamp*1000000)
        timestamps.append(timestamp_16decimalplace)

        frame_time+=addtime
    
    return timestamps

def save_metadata_for_multiplexer(metadata,save_path_name):
    metadata.insert(0,['Precision Time Stamp','Sensor Latitude','Sensor Longitude','Platform Heading Angle','Platform Pitch Angle','Platform Roll Angle',\
                       'Sensor Ellipsoid Height','Sensor Horizontal Field of View','Sensor Vertical Field of View','Sensor Relative Azimuth Angle','Sensor Relative Elevation Angle','Sensor Relative Roll Angle'])
    ##在0索引处添加字段名。（来自于orbslam3位姿读取_利用截取的文件.py）
##Arcgis Pro 视频多路复用器的12个参数
    #文心一言# ##来自于orbslam3位姿读取_利用截取的文件.py
    with open(save_path_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
        # 写入数据
        for row in metadata:#groundtruth列表中的每一行分别写入
            writer.writerow(row)
    #文心一言#
    ##文心一言：# 文件在with块结束时自动关闭
    print("已成功保存，路径：",save_path_name)


snippet_path_name='D:\无人机项目 2025\gis数据集\DJI_20241227144107_0002_D(资料四)//DJI_20241227144107_0002_D_log.csv'
#snippet_path_name='D:\无人机项目\无人机资料解析\蒋志承遥控器资料\csv//Jun-17th-2024-05-42PM-Flight-Airdata (1).csv'
lens_type='FC8282'#DJIAir3广角# #资料四：model_name:FC8282; 

record_df=pd.read_csv(snippet_path_name)
print("记录总条数：",len(record_df))
record_by_seconds=get_record_by_seconds(record_df)

print("每一秒的记录情况：",record_by_seconds)

timestamps=make_timestamp(len(record_by_seconds[0]),record_df)
print(timestamps)

Sensor_Latitude=record_df["latitude"].tolist()
Sensor_Longitude=record_df["longitude"].tolist()

##杭州的磁偏角：杭州3°50'w  
magnetic_declination=convert_dms_to_decimal(-3,-50,0)##算角度时就用负数  #杭州#
print("磁偏角：",magnetic_declination)
Platform_Heading_Angle=[]
for x in record_df[" compass_heading(degrees)"]:
    heading_angle=x + magnetic_declination##加上反方向的影响
    ##磁偏角就是一个基准，向西偏（或者说，向逆时针偏）就是基准本身为负。所以要加上基准，或者减掉向西偏导致的多出来的角度。
    if heading_angle<0:
        heading_angle+=360##如果是负数则加上360变成360度标准的方位角
        #元数据标准这样规定：
        #Aircraft heading relative to True North, measured clockwise in the horizontal plane looking down. 
        # 虽然是罗盘朝向，但是方向规定是“真北” ，所以要进行磁偏角校正
        # Compass direction, range 0.0 to 360.0
        #元数据标准要求是360度标准的方位角
    Platform_Heading_Angle.append(heading_angle)
print("经过磁偏角校正和转换为0~360角度标准后的平台朝向角：",Platform_Heading_Angle)

Platform_Pitch_Angle=record_df[" pitch(degrees)"].tolist()##朝上为正，不一定是正数
Platform_Roll_Angle=record_df[" roll(degrees)"].tolist()##理由同上
#horizontal plane with positive angles for left wing above the horizontal plane 无人机左翼高过水平面为正

altitude=[record_df.iloc[i]['altitude_above_seaLevel(feet)']* 0.3048 for i in range(len(record_df)) ]
##传感器高度的单位是Meters，见D:\Program Files\GeoScene\Pro\Resources\MotionImagery//FMV_Multiplexer_Field_Mapping_Template.csv文件中的（D,15）
#要把英尺转成米 meters = feet * 0.3048  ##

if lens_type=='FC8282':##根据2025年2月20号的计算结果
    hfov="65.6"##水平视场角
    vfov="36.9"##垂直视场角
elif lens_type=='FC8284':##根据2025年2月20号的计算结果
    hfov='28'
    vfov='15.75'
#hfovs=[hfov*len(record_df)]
#vfovs=[vfov*len(record_df)]
#print("水平视场角列表：",hfovs)

#KIMI#
#是的，Sensor Relative Azimuth Angle（传感器相对方位角）确实是指传感器（例如相机或传感器平台）相对于平台本身的朝向角。
# 它描述的是传感器的指向方向相对于平台纵轴（通常是指飞行器的飞行方向）的角度。
relative_azimuth_to360=[angle + 360 if angle < 0 else angle for angle in [record_df.iloc[i]['gimbal_heading(degrees)']-(record_df.iloc[i][" compass_heading(degrees)"]+magnetic_declination) for i in range(len(record_df))]]
##是要加带正负号的磁偏角，因为磁偏角是一个基准，理由同平台朝向角的计算。
#使用列表推导式可以非常简洁地实现将一个列表中的角度从 -180°~180° 转换为 0°~360°。具体方法是：如果角度小于 0，则加上 360 度。
#KIMI#
print("换成360度的云台相对方位角：",relative_azimuth_to360)

#KIMI#
'''
关于 Sensor Relative Elevation Angle 的计算
1. 定义与计算方法
Sensor Relative Elevation Angle（传感器相对仰角）是指云台（gimbal）相对于无人机平台水平面的仰角。它描述的是云台相对于无人机平台的垂直方向偏移。
根据大疆公司的说明：
gimbal_pitch（云台俯仰角）是以水平面为基准的角度，范围通常是 -90° 到 +90°。
pitch（无人机俯仰角）也是以水平面为基准的角度，范围同样是 -90° 到 +90°。
因此，Sensor Relative Elevation Angle 可以通过以下公式计算：
Python
复制
Sensor Relative Elevation Angle = gimbal_pitch - pitch

Sensor Relative Elevation Angle：
描述的是云台相对于无人机平台水平面的仰角。
它是云台角度与无人机平台角度的差值，表示云台相对于无人机平台的相对仰角。
即云台相对于无人机平台的垂直偏移。
'''
#KIMI#
relative_elevation=[record_df.iloc[i]['gimbal_pitch(degrees)']-record_df.iloc[i][' pitch(degrees)'] for i in range(len(record_df))]
##云台和机身的角度差基本不可能超过+=180 而且没要求360度标准，因此暂时不进行其他考虑

#Sensor Relative Roll Angle的标准：
# Relative roll angle of sensor to aircraft platform. Top of image level is zero degrees. Positive angles are clockwise when looking from behind camera. 
relative_roll=[record_df.iloc[i]['gimbal_roll(degrees)']-record_df.iloc[i][' roll(degrees)'] for i in range(len(record_df))]
##不进行其他考虑同上

metadata=[[timestamps[i],Sensor_Latitude[i],Sensor_Longitude[i],Platform_Heading_Angle[i],Platform_Pitch_Angle[i],Platform_Roll_Angle[i],\
           altitude[i],hfov,vfov,relative_azimuth_to360[i],relative_elevation[i],relative_roll[i]] for i in range(len(record_df))]

save_path_name='D:\无人机项目 2025\gis数据集\DJI_20241227144107_0002_D(资料四)//DJI_20241227144107_0002_D_log_metadata_for_multiplexer.csv'
save_metadata_for_multiplexer(metadata,save_path_name)

'''
资料一：
snippet_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617172347_0010_D(资料一)//DJI_20240617172347_0010_D_log.csv'
lens_type='FC8282'
magnetic_declination=convert_dms_to_decimal(-3,-50,0)##算角度时就用负数
save_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617172347_0010_D(资料一)//DJI_20240617172347_0010_D_log_metadata_for_multiplexer.csv'
'''

'''
snippet_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617174322_0014_D(资料三)//DJI_20240617174322_0014_D_log.csv'
lens_type='FC8282'#资料二：model_name:FC8282; #DJIAir3广角#
magnetic_declination=convert_dms_to_decimal(-3,-50,0)##算角度时就用负数  #杭州#
save_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617174322_0014_D(资料三)//DJI_20240617174322_0014_D_log_metadata_for_multiplexer.csv'
'''