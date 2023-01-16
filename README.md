<h1 align="center">- Bilibili(B站)全弹幕获取程序 -</h3>

<p align="center">
<img src="https://img.shields.io/github/v/release/DNLINYJ/Biilibili_All_Danmu.svg?logo=iCloud">
</p>

## 喜欢或者对您有用的话就给颗Star吧，您的支持是我维护的最大动力(′･ω･`)

# 准备
1. Python 3 及以上版本

2. 安装依赖
    ```sh
    pip install -r requirements.txt
    ```
3. 配置

    运行 ``python main.py``, 首次使用需要输入自己的SESSDATA，
    SESSDATA **经Base64编码后** 保存至 `.config` 文件。

# 功能

|功能                                  |描述                                     |
|-------------------------------------|-----------------------------------------|
|收集指定视频全部历史弹幕               |获取指定视频自发布之日起的所有弹幕         |
|导出数据库内指定视频全部历史弹幕       |导出数据库内指定视频所保存的全部历史弹幕    |
|收集并导出指定视频全部历史弹幕         |获取指定视频自发布之日起的所有弹幕并导出(数据量较大时所用时间较久,谨慎使用)|

# 使用
```sh
python3 main.py
```

# 问题
1. 什么是SESSDATA? 怎么获取我自己的SESSDATA?

> 答：SESSDATA相当于您Bilibili账号的通行凭证，我们只会将您的SESSDATA用于获取历史弹幕相关的信息。若不了解如何获取自己的SESSDATA，请看[教程](https://www.bilibili.com/read/cv12349604)。

2. SESSDATA格式不正确是什么原因?
> 答：SESSDATA格式如下(以下SESSDATA已失效)，请检查您的SESSDATA格式是否于下方一致,若还有疑问可以提出 Issues
>> SESSDATA=560f605d%2C1570783582%2C9881e691

3. 为什么在收集弹幕数据的时候会出现失败的情况?
> 答：收集弹幕数据的时候会出现失败的情况主要为：收集数据的视频发布时间过久，请求历史弹幕数据的次数过多，导致B站服务器拒绝访问，建议15分钟后再次尝试。若出现其他问题，请将报错信息以及使用的库、Python版本一并提交Issues。

4. 报错终止运行了怎么办?
> 答：请将报错信息以及使用的库、Python版本一并提交Issues。

5. 为什么成功获取了视频的所有弹幕，导出后的弹幕数量与B站视频页面的不一致?
> 答：这个问题还没有一个确切的答案，目前的猜测是当某一天的弹幕池内弹幕数量超过1000条时，B站的API只会给你返回1000条弹幕，这个我也没办法¯\\\_(ツ)_/¯

# 性能展示
![9.5万条弹幕获取测试](https://github.com/DNLINYJ/Biilibili_All_Danmu/blob/master/Photos/9.5%E4%B8%87%E6%9D%A1%E5%BC%B9%E5%B9%95%E8%8E%B7%E5%8F%96%E6%B5%8B%E8%AF%95-1.png "9.5万条弹幕获取测试")

![9.5万条弹幕导出测试](https://github.com/DNLINYJ/Biilibili_All_Danmu/blob/master/Photos/9.5%E4%B8%87%E6%9D%A1%E5%BC%B9%E5%B9%95%E5%AF%BC%E5%87%BA%E6%B5%8B%E8%AF%95.png "9.5万条弹幕导出测试")

# LICENSE

[Apache-2.0 License](https://github.com/DNLINYJ/Biilibili_All_Danmu/blob/master/LICENSE)

# 致谢

> [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)  
