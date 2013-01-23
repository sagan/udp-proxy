udp-proxy
=========

A simple encrypted udp proxy in python

一个用Python写的简单的UDP代理，由服务器端(udp_server.py)和客户端(udp_client.py)两部分组成。参考shadowsocks的代码对传输数据做了简单混淆。

由于UDP的限制，一个服务端只能与一个客户端连接。

写这个东西的初衷是用来封装OpenVPN的UDP流量，避免被GFW检测到和干扰 - -

使用方法
---------

使用方式和obfsproxy类似，只不过这个是UDP的。

以OpenVPN为例：

假设在IP是1.2.3.4的国外服务器上架设了OpenVPN Server，监听1194 UDP端口。

在1.2.3.4上运行：
	
	./udp_server.py -s 1.2.3.4 -p 1194 -l 7070 -k "foobar"


在OpenVPN客户端机器上运行：
	
	./udp_client.py -s 1.2.3.4 -p 7070 -l 7071 -k "foobar"


"foobar"是自定义的密码，服务器端和客户端需要相同。


然后修改OpenVPN客户端的配置文件：

将
	remote 1.2.3.4 1194

改为

	remote 127.0.0.1 7071

注释掉"redirect-gateway def1"这行（如果OpenVPN服务器有push "redirect-gateway def1"也要去掉），然后增加下面几行：

	route 1.2.3.4 255.255.255.255 net_gateway
	route 0.0.0.0 128.0.0.0 192.168.245.1
	route 128.0.0.0 128.0.0.0 192.168.245.1


这样就可以了。








	
		




