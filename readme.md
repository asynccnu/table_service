# table_service

> 华师匣子课表查询服务

## 环境配置(container.env)

    XNM=2014 // 表示2014~2015学年, 类推
    XQM=3    // 3: 第1学期, 12: 第2学期, 16: 第3学期

    MONGOHOST=localhost // mongodb host
    MONGOPORT=27017     // mongodb port
	ADMIN_SID=szkc admin username
	ADMIN_PWD=szkc admin password 

## 部署

**单独部署**:

```shell
$ docker-compose stop && docker-compose build && dockder-compose up -d &&
docker-compose ps
```

## Log

+ 2017年4月29日: 拖了2个月了...ㄟ( ▔, ▔ )ㄏ
+ 2018年3月20日: 在课表中增加了素质课
