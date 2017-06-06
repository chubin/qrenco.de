## Usage

The service is used to generate QR-codes for strings in a UNIX/Linux console
using curl/httpie/wget or similar tools. 

![qrenco.de usage](http://igor.chub.in/download/qrenco.de.png)

The service can be used in a browser also.
Just add `qrenco.de/` before the URL.

![qrenco.de in browser](http://igor.chub.in/download/qrenco.de-browser.png)

The service uses [libqrencode](https://github.com/fukuchi/libqrencode) to generate QR-codes.

## Installation 

You don't need to install the service for using it (just try curl qrenco.de),
but if you want to install it locally, do the following steps:

```
	$ git clone https://github.com/chubin/qrenco.de
        $ cd qrenco.de
	$ virtualenv ve
	$ ve/bin/pip install -r requirements.txt
	$ sudo apt-get install libqrenv
	$ ve/bin/python bin/srv.py
```

If you want to use a HTTP-frontend for the service,
configure it this way:

```
server {
    listen 80;
    listen [::]:80;
    server_name  qrenco.de *.qrenco.de;
    access_log  /var/log/nginx/qrenco.de-access.log;
    error_log  /var/log/nginx/qrenco.de-error.log;

    location / {
        proxy_pass         http://127.0.0.1:8003;

        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $remote_addr;

        client_max_body_size       10m;
        client_body_buffer_size    128k;

        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;

        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;

        expires                    off;
    }

}

```
