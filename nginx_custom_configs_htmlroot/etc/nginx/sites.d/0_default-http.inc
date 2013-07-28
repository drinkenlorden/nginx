########################################################################
### HTTPS Defaults #####################################################
########################################################################

server {
    listen       0.0.0.0:443 default_server deferred backlog=1024;
    include      inc/ssl-_.example.com.conf;
    include sites.d/0_default-http.subinc;
}
########################################################################
### HTTP Defaults for loopback #########################################
########################################################################

server {
    listen       0.0.0.0:80 default_server deferred backlog=1024;
    include sites.d/0_default-http.subinc;
}
