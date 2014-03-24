#   社交网络信息融合-文档-数据结构篇

##  概述

+   由于信息融合需要收集大量原始数据，除了需要使用自定义数据结构之外，还需要大量使用关系数据库来存储 收集到的原始数据以用作分析。
+   处于方便和查询性能考虑， **数据采集阶段** 使用sqlite3作为关系数据库来使用，存储采集到的原始数据。
+   待添加


##  详细数据结构

### 数据采集阶段

1.  主数据表/user_info
    | 字段名（含义）/数据来源 | 字段类型    | 彼岸  | 微博  | QQ空间 |
    |-------------------------|-------------|-------|-------|--------|
    |user_name/用户名         |VCHAR(255)   |       |       |        |
    |uid/用户唯一id           |VCHAR(255)   |       |       |        |
    |email/用户邮箱           |VCHAR(255)   |       |       |        |
    |qq/QQ号码                |CHARACTER(20)|       |       |        |
    |home/所属地区            |VCHAR(255)   |       |       |        |
###删除|messages/发言（消息）    |One to Many  |       |       |        |
    |care_about/关注          |LONGTEXT         |   x   |       |        |
    |fans/粉丝                |LONGTEXT,用','分割|   x  |       |   x    |
    |pk/唯一序号              |INTEGER(pk)  |       |       |        |
    |tags/标签                |TEXT，','分割|   x   |       |        |
    |clocation/当前地理位置   |TEXT         |   x   |       |        |
    |wei_level/微博会员等级   |int          |
    |vip_level/vip等级        |int
    |sex                      |int (0女，1为男)|
2.  发言数据表/messages
    | 字段名（含义）/ | 字段类型 |
    |-----------------|----------|
    |mid/发言id       | INTEGER(pk)  |
    |p_time/发表时间  | DATETIME |
    |content/内容     | TEXT     |
    |tags/内容标签    | TEXT,‘,’分割 |
    |is_forward/是否转发| BOOL   |
###删除|releated_uname/相关用户名（如被@)|     |
    |uid_u            | VCHAR(20)     |
