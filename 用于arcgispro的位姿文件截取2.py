import datetime
import pandas as pd
import re
from pytz import timezone, utc


#zhihu zhida#
def slice_csv_pandas(input_file, output_file, start_row, end_row):
    # 读取 CSV 文件（自动处理表头）
    df = pd.read_csv(input_file)
    
    # 切片操作（包含 start_row 到 end_row 行）
    sliced_df = df.iloc[start_row:end_row+1]
    
    # 保存新文件（保留原表头）
    sliced_df.to_csv(output_file, index=False)

#zhihu zhida#

#def readvideotime(videoname): 

#zhihu zhida#
def extract_video_time(filename, source_tz='Asia/Shanghai'):
    """
    从文件名提取时间并转换为UTC时间的datetime对象
    
    :param filename: 视频文件名
    :param source_tz: 原始时区，默认为'Asia/Shanghai'
    :return: 转换为UTC时间的datetime对象
    """
    match = re.search(r'_(\d{14})_', filename)
    if not match:
        raise ValueError("文件名格式错误")
    
    time_str = match.group(1)
    naive_dt = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S")
    
    # 添加原始时区信息并转换UTC
    localized_dt = timezone(source_tz).localize(naive_dt)
    return localized_dt.astimezone(utc)
'''
默认时区：

默认使用source_tz='Asia/Shanghai'
参数灵活性：

用户可以传递任何有效的时区字符串给source_tz参数。
返回值：

函数始终返回一个带有UTC时区信息的datetime对象。
'''
#zhihu zhida#

def find_log_start(record_df,stt_time):
    '''为了避免这个错误，你需要确保 possiblestartrecord 在函数中始终被赋值。
    可以通过在函数开头初始化 possiblestartrecord 来解决这个问题。'''
    possiblestartrecord = None  # 初始化为 None 或其他默认值
    truestartrecord=0##先初始化不然会报错

    stt_time_utc = stt_time.replace(microsecond=0)  # 忽略微秒信息  #KIMI##

    for i in range(len(record_df)):#对所有记录进行循环
        record_time = pd.to_datetime(record_df.values[i][1])#取出每一行的时间信息

        #record_time_utc = record_time.tz_localize('UTC', ambiguous='infer')  # 转换为 UTC 时间  #KIMI##
        #Cannot infer offset with only one time.
        record_time = record_time.tz_localize('UTC')  # record_time添加 UTC 时区信息

        # record_time  转换为 datetime.datetime 格式
        record_time_dttm = record_time.to_pydatetime()

        
        if record_time_dttm == stt_time_utc:####转换成统一格式以后再比较   #KIMI## #record_time本身就是世界时
            #问题:时间格式不统一导致无法正常判断相等
            #原因及解决:
            '''#KIMI#
            在你的代码中，record_time 是一个 pandas.Timestamp 类型，而 stt_time 是一个带时区信息的 datetime.datetime 类型。由于它们的类型和时区信息不同，直接比较会导致问题。
        为了有效比较这两个变量表示的时间，你需要将它们转换为相同的时间格式和时区。以下是解决方案：
        1. 将 record_time 转换为 UTC 时间
        record_time 是一个 pandas.Timestamp，默认情况下可能没有时区信息。你可以将其转换为 UTC 时间，然后与 stt_time 进行比较。
        2. 比较时间时忽略微秒
        stt_time 中包含微秒信息（tzinfo=<UTC>），而 record_time 可能没有。为了比较，可以忽略微秒信息。
            #KIMI#'''
            possiblestartrecord=i
            #KIMI#
            break  # 找到匹配的时间后退出循环

    if possiblestartrecord is None:
        raise ValueError("未找到匹配的开始时间")
    #KIMI#

    #for i in range(61):##前后三秒钟的记录进行扫描
    if record_df.iloc[possiblestartrecord]['isVideo']==0:##如果
        for i in range(possiblestartrecord,possiblestartrecord+50):#从可能位置往后找50行
            if record_df.iloc[i]['isVideo']==1:
                truestartrecord=i
                break##找到以后退出

    elif record_df.iloc[possiblestartrecord]['isVideo']==1:
        for i in range(possiblestartrecord,possiblestartrecord-50,-1):#从可能位置往前找50行
            if record_df.iloc[i]['isVideo']==0:
                truestartrecord=i+1##如果在前面找到0，则说明下一行开始
                ##若possiblestartrecord正好是开始的记录，则上一行是0，则+1以后还是回到这一行。
    ####如果开始时间距离飞行日志开头和结尾不足5秒，可能会出错。但是大多数情况录像不会和飞行日志的起始和结束挨得那么紧。
                break

    for i in range(truestartrecord,len(record_df)):
        if record_df.iloc[i]['isVideo']==0:
            endrecord=i-1
            #在后面找到0，要减1。和上面那个找开始行找到0然后的处理方法类似但相反。
            # 因为：isVideo==0的行已经超过视频相关行一行了。
            # 想要得到真正的最后一行，就要在最后找到0以后回到上一行，上一行才是isVideo为1的最后一行
            break
    return truestartrecord,endrecord


#possiblestartrecord=0

#资料相关信息#
csvpath='D:\无人机项目\无人机资料解析\蒋志承遥控器资料\csv'
csvname='Dec-27th-2024-02-36PM-Flight-Airdata.csv'#csvpath_name 这是完整文件名+文件路径
video_name='DJI_20241227144107_0002_D.MP4'
output_path_name='D:\无人机项目 2025\gis数据集\DJI_20241227144107_0002_D(资料四)//DJI_20241227144107_0002_D_log.csv'
#资料相关信息#

csvpath_name=csvpath+'//'+csvname

record_df = pd.read_csv(csvpath_name)
stt_time=extract_video_time(video_name)
print("文件显示的开始时间是：",stt_time)
startrecord,endrecord=find_log_start(record_df,stt_time)
print("实际开始时间：",record_df.values[startrecord][1])
print("实际结束时间：",record_df.values[endrecord][1])
print("程序中的开始行是(从0开始)：",startrecord)
print("程序中的结束行是(从0开始)：",endrecord)
print("拍摄时间为",(endrecord-startrecord)/10,"秒")
slice_csv_pandas(csvpath_name,output_path_name,startrecord,endrecord)
print("已成功截取开始行和结束行之间的记录！")


'''
在 Pandas 中处理 CSV 文件时，索引值与 CSV 文件中显示的行数之间的关系可以这样理解：
CSV 文件中的行数与 Pandas 索引的关系：
CSV 文件中的行数是从 1 开始计数 的，包括表头（字段名）那一行。
Pandas 的索引是从 0 开始计数 的，且不包括表头那一行。
因此，如果 CSV 文件中显示的行数为 n，那么在 Pandas DataFrame 中对应的索引值为 n - 2。

csv表格中的第二行相当于本程序record_df当中的第0行。因此：
    如果 CSV 文件中显示的行数为 n（从 1 开始计数），那么在 Pandas DataFrame 中对应的索引值为：
索引值 = n - 2
'''

'''
资料一 相关信息：
csvpath='D:\无人机项目\无人机资料解析\蒋志承遥控器资料\csv'
csvname='Jun-17th-2024-05-22PM-Flight-Airdata.csv'#csvpath_name 这是完整文件名+文件路径
video_name='DJI_20240617172347_0010_D.MP4'
output_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617172347_0010_D(资料一)//DJI_20240617172347_0010_D_log.csv'
'''
#对于DJI_20240617172347_0010_D.MP4(资料一)的相关记录（在飞行日志文件Jun-17th-2024-05-22PM-Flight-Airdata.csv当中）来说：
# 以记录行的isVideo为1为标准，在csv文件当中的行数为:826~886
#因此，在本程序的record_df当中的行数应该是:824~884

'''
资料三：
csvpath='D:\无人机项目\无人机资料解析\蒋志承遥控器资料\csv'
csvname='Jun-17th-2024-05-42PM-Flight-Airdata (1).csv'#csvpath_name 这是完整文件名+文件路径
video_name='DJI_20240617174322_0014_D.MP4'
output_path_name='D:\无人机项目 2025\gis数据集\DJI_20240617174322_0014_D(资料三)//DJI_20240617174322_0014_D_log.csv'

件显示的开始时间是： 2024-06-17 09:43:22+00:00
实际开始时间： 2024-06-17 09:43:23
实际结束时间： 2024-06-17 09:43:49
程序中的开始行是(从0开始)： 543
程序中的结束行是(从0开始)： 804
拍摄时间为 26.1 秒
'''

'''
资料四：
csvpath='D:\无人机项目\无人机资料解析\蒋志承遥控器资料\csv'
csvname='Dec-27th-2024-02-36PM-Flight-Airdata.csv'#csvpath_name 这是完整文件名+文件路径
video_name='DJI_20241227144107_0002_D.MP4'
output_path_name='D:\无人机项目 2025\gis数据集\DJI_20241227144107_0002_D(资料四)//DJI_20241227144107_0002_D_log.csv'

文件显示的开始时间是： 2024-12-27 06:41:07+00:00
实际开始时间： 2024-12-27 06:41:09
实际结束时间： 2024-12-27 06:41:29
程序中的开始行是(从0开始)： 3193
程序中的结束行是(从0开始)： 3394
拍摄时间为 20.1 秒
'''