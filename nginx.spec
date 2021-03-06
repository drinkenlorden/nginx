%bcond_without nginx_module_vts
%bcond_without ngx_dynamic_upstream
%bcond_without headers_more
%bcond_without lua
%bcond_without mod_security
%bcond_without ldap


# We need to compile it separatelly
# sudo yum install httpd httpd-devel pcre pcre-devel
# cd ~/rpmbuild/SOURCES
# git clone https://github.com/SpiderLabs/ModSecurity.git mod_security
# cd mod_security
# ./autogen.sh
# ./configure --enable-standalone-module
# make


%bcond_with lua_upstream_nginx_module
%bcond_with ngx_http_dyups

# Cannot patch
%bcond_with nginx_limit_upstream

#%%global commit c5a4525bfa3bd9997834d0603c40093e50e3fd19
#%%global shortcommit %(c=%{commit}; echo ${c:0:7})
#For the        source tarball, you should use this syntax:
#Source0:        https://github.com/$OWNER/$PROJECT/archive/%{commit}/%{name}-%{version}.tar.gz
##%%prep
##%%setup -qn %{name}-%{commit}

%define headers_more_version 0.261
%define lua_nginx_version 0.9.16
%define ngx_devel_kit_version 0.2.19
%define nginx_limit_upstream_version 1.1.0

%global  _hardened_build     1
%global  nginx_user          nginx
%global  nginx_group         %{nginx_user}
%global  nginx_home          %{_localstatedir}/lib/nginx
%global  nginx_home_tmp      %{nginx_home}/tmp
%global  nginx_confdir       %{_sysconfdir}/nginx
%global  nginx_datadir       %{_datadir}/nginx
%global  nginx_logdir        %{_localstatedir}/log/nginx
%global  nginx_webroot       %{nginx_datadir}/html

# gperftools exist only on selected arches
%ifarch %{ix86} x86_64 ppc ppc64 %{arm}
%global  with_gperftools     1
%endif

# AIO missing on some arches
%ifnarch aarch64
%global  with_aio   1
%endif

Name:              nginx
Epoch:             123
Version:           1.9.5
Release:           11.SS%{?dist}

Summary:           A high performance web server and reverse proxy server
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
URL:               http://nginx.org/

Source0:           http://nginx.org/download/nginx-%{version}.tar.gz
Source1:           http://nginx.org/download/nginx-%{version}.tar.gz.asc
Source10:          nginx.service
Source11:          nginx.logrotate
Source12:          nginx.conf
Source13:          nginx-upgrade
Source14:          nginx-upgrade.8
Source100:         index.html
Source101:         poweredby.png
Source102:         nginx-logo.png
Source103:         404.html
Source104:         50x.html

# SS
Source1001: https://github.com/yzprofile/ngx_http_dyups_module/archive/master.tar.gz#/ngx_http_dyups_module.tar.gz

Source1008:  https://github.com/vozlt/nginx-module-vts/archive/master.tar.gz#/nginx-module-vts.tar.gz

#Source1009:  https://github.com/cubicdaiya/ngx_dynamic_upstream/archive/v0.1.1.tar.gz#/ngx_dynamic_upstream-0.1.1.tar.gz
Source1009: https://github.com/cubicdaiya/ngx_dynamic_upstream/archive/master.tar.gz#/ngx_dynamic_upstream-master.tar.gz

#Source1010: https://github.com/cfsego/nginx-limit-upstream/archive/v{nginx_limit_upstream_version}.tar.gz#/nginx-limit-upstream.tar.gz
Source1010: https://github.com/cfsego/nginx-limit-upstream/archive/master.tar.gz#/nginx-limit-upstream.tar.gz

Source1011:  https://github.com/openresty/lua-upstream-nginx-module/archive/master.tar.gz#/lua-upstream-nginx-module.tar.gz

Source1012:  https://github.com/simpl/ngx_devel_kit/archive/v%{ngx_devel_kit_version}.tar.gz#/ngx_devel_kit-%{ngx_devel_kit_version}.tar.gz
Source1013:  https://github.com/openresty/lua-nginx-module/archive/v%{lua_nginx_version}.tar.gz#/lua-nginx-module-%{lua_nginx_version}.tar.gz

#Source1014:  http://github.com/agentzh/headers-more-nginx-module/tarball/v0.14/agentzh-headers-more-nginx-module-v0.14-0-g2cbbc15.tar.gz
Source1014:  https://github.com/openresty/headers-more-nginx-module/archive/v%{headers_more_version}.tar.gz#/gentzh-headers-more-nginx-module.tar.gz

Source1015: https://github.com/kvspb/nginx-auth-ldap/archive/master.tar.gz#/nginx-auth-ldap.tar.gz

Patch100:    https://github.com/drinkenlorden/nginx/raw/d71c09533989ce2881178ecd5a13aae99e056ee7/request_start_variable.patch

# SS \

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:            nginx-auto-cc-gcc.patch

BuildRequires:     GeoIP-devel
BuildRequires:     gd-devel
%if 0%{?with_gperftools}
BuildRequires:     gperftools-devel
%endif
BuildRequires:     libxslt-devel
BuildRequires:     openssl-devel
BuildRequires:     pcre-devel
BuildRequires:     perl-devel
BuildRequires:     perl(ExtUtils::Embed)
BuildRequires:     zlib-devel
BuildRequires:     lua-devel
BuildRequires:     openldap-devel

Requires:          lua
Requires:          nginx-filesystem = %{epoch}:%{version}-%{release}
Requires:          GeoIP
Requires:          gd
Requires:          openssl
#Requires:          openldap

Requires:          pcre
Requires:          perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires(pre):     nginx-filesystem
Provides:          webserver

BuildRequires:     systemd
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd

%description
Nginx is a web server and a reverse proxy server for HTTP, SMTP, POP3 and
IMAP protocols, with a strong focus on high concurrency, performance and low
memory usage.

%package filesystem
Group:             System Environment/Daemons
Summary:           The basic directory layout for the Nginx server
BuildArch:         noarch
Requires(pre):     shadow-utils

%description filesystem
The nginx-filesystem package contains the basic directory layout
for the Nginx server including the correct permissions for the
directories.


%prep
%setup -q
%patch0 -p0
%patch100 -p0

%if %{with ngx_http_dyups}
tar -xzf "%{SOURCE1001}"
mv ngx_http_dyups_module* ngx_http_dyups_module || :
%endif

%if %{with nginx_module_vts}
tar -xzf "%{SOURCE1008}"
mv nginx-module-vts* nginx-module-vts || :
%endif

%if %{with ngx_dynamic_upstream}
tar zxf "%{SOURCE1009}"
mv ngx_dynamic_upstream-master* ngx_dynamic_upstream-master || :
%endif

%if %{with nginx_limit_upstream}
tar -xzf "%{SOURCE1010}"
# If we have master instead tag, then unify
mv nginx-limit-upstream* nginx-limit-upstream || :
patch -p1 < ./nginx-limit-upstream/nginx-1.4.4.patch
#patch -p1 < ./nginx-limit-upstream/nginx.patch
%endif

%if %{with lua_upstream_nginx_module}
mkdir lua-upstream-nginx-module
tar -C lua-upstream-nginx-module -xzf "%{SOURCE1011}"
%endif

%if %{with lua}
mkdir lua-nginx-module-%{lua_nginx_version}
#%{__tar} C lua-nginx-module-%{lua_nginx_version} xzvf "%{SOURCE1013}"

tar -C lua-nginx-module-%{lua_nginx_version} -xzvf "%{SOURCE1013}"


%setup -T -D -a 1013
#%setup -c -a 2 -D -n nginx-%{version}/ngx_devel_kit-%{ngx_devel_kit_version}

mkdir ngx_devel_kit-%{ngx_devel_kit_version}
#%{__tar} C ngx_devel_kit-%{ngx_devel_kit_version}  xzvf "%{SOURCE1012}"
tar -C ngx_devel_kit-%{ngx_devel_kit_version}  -xzvf "%{SOURCE1012}"
%setup -T -D -a 1012
#%%setup -c -a 2 -D -n nginx-%{version}/ngx_devel_kit-%{ngx_devel_kit_version}
%endif

%if %{with headers_more}
mkdir headers_more
tar -C headers_more -xzf "%{SOURCE1014}"
mv headers_more/*/* headers_more/
%endif

%if %{with ldap}
tar -xzf "%{SOURCE1015}"
mv nginx-auth-ldap* nginx-auth-ldap || :
%endif


#sed -i 's|^static char ngx_http_server_string[] = "Server.*|static char ngx_http_server_string[] = "Server: nginx@ssabchew.info" CRLF;' src/http/ngx_http_header_filter_module.c 
#sed -i 's|^static char ngx_http_server_full_string[] = "Server.*|static char ngx_http_server_full_string[] = "Server: nginx@ssabchew.info" NGINX_VER CRLF;|' src/http/ngx_http_header_filter_module.c


%build

# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.
export DESTDIR=%{buildroot}
export LUA_LIB=/usr/lib64
export LUA_INC=/usr/share/lua/5.1
export DESTDIR=%{buildroot}

./configure \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/nginx \
    --conf-path=%{nginx_confdir}/nginx.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --http-uwsgi-temp-path=%{nginx_home_tmp}/uwsgi \
    --http-scgi-temp-path=%{nginx_home_tmp}/scgi \
    --pid-path=/run/nginx.pid \
    --lock-path=/run/lock/subsys/nginx \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
%if 0%{?with_aio}
    --with-file-aio \
%endif
    --with-ipv6 \
    --with-http_ssl_module \
    --with-http_v2_module  \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_xslt_module \
    --with-http_image_filter_module \
    --with-http_geoip_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_stub_status_module \
    --with-http_perl_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-pcre \
    --with-pcre-jit \
    --with-http_auth_request_module \
%if 0%{?with_gperftools}
    --with-google_perftools_module \
%endif
%if %{with ngx_http_dyups}
    --add-module="$PWD/ngx_http_dyups_module" \
%endif
%if %{with nginx_limit_upstream}
    --add-module="$PWD/nginx-limit-upstream" \
%endif
%if %{with lua_upstream_nginx_module}
    --add-module="$PWD/lua-upstream-nginx-module" \
%endif
%if %{with lua}
     --add-module=/$PWD/ngx_devel_kit-%{ngx_devel_kit_version} \
     --add-module=/$PWD/lua-nginx-module-%{lua_nginx_version} \
%endif
%if %{with ngx_dynamic_upstream}
    --add-module=/$PWD/ngx_dynamic_upstream-master  \
%endif
%if %{with nginx_module_vts}
    --add-module="$PWD/nginx-module-vts" \
%endif
%if %{with headers_more}
    --add-module="$PWD/headers_more" \
%endif
%if %{with mod-security}
    --add-module="~/rpmbuild/SOURCES/mod_security" \
%endif
%if %{with ldap}
    --add-module="$PWD/nginx-auth-ldap" \
%endif
    --with-debug \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols


### May be move to this convention?
##     --add-module=%{_builddir}/%{name}-%{version}/ngx_devel_kit-%{ngx_devel_kit_version} \
##     --add-module=%{_builddir}/%{name}-%{version}/lua-nginx-module-%{lua_nginx_version} \

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;
install -p -D -m 0644 %{SOURCE10} \
    %{buildroot}%{_unitdir}/nginx.service

install -p -D -m 0644 %{SOURCE11} \
    %{buildroot}%{_sysconfdir}/logrotate.d/nginx

install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/default.d
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/pki
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/sites.d
install -p -d -m 0700 %{buildroot}%{nginx_home}
install -p -d -m 0700 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0700 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}

install -p -m 0644 %{SOURCE12} \
    %{buildroot}%{nginx_confdir}
install -p -m 0644 %{SOURCE100} \
    %{buildroot}%{nginx_webroot}
install -p -m 0644 %{SOURCE101} %{SOURCE102} \
    %{buildroot}%{nginx_webroot}
install -p -m 0644 %{SOURCE103} %{SOURCE104} \
    %{buildroot}%{nginx_webroot}

install -p -D -m 0644 %{_builddir}/nginx-%{version}/man/nginx.8 \
    %{buildroot}%{_mandir}/man8/nginx.8

install -p -D -m 0755 %{SOURCE13} %{buildroot}%{_bindir}/nginx-upgrade
install -p -D -m 0644 %{SOURCE14} %{buildroot}%{_mandir}/man8/nginx-upgrade.8

for i in ftdetect indent syntax; do
    install -p -D -m644 contrib/vim/${i}/nginx.vim \
        %{buildroot}%{_datadir}/vim/vimfiles/${i}/nginx.vim
done


%pre filesystem
getent group %{nginx_group} > /dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} > /dev/null || \
    useradd -r -d %{nginx_home} -g %{nginx_group} \
    -s /sbin/nologin -c "Nginx web server" %{nginx_user}
exit 0

%post
%systemd_post nginx.service

%preun
%systemd_preun nginx.service

%postun
%systemd_postun nginx.service
if [ $1 -ge 1 ]; then
    /usr/bin/nginx-upgrade >/dev/null 2>&1 || :
fi

%files
%doc LICENSE CHANGES README
%{nginx_datadir}/html/*
%{_bindir}/nginx-upgrade
%{_sbindir}/nginx
%{_datadir}/vim/vimfiles/ftdetect/nginx.vim
%{_datadir}/vim/vimfiles/syntax/nginx.vim
%{_datadir}/vim/vimfiles/indent/nginx.vim
%{_mandir}/man3/nginx.3pm*
%{_mandir}/man8/nginx.8*
%{_mandir}/man8/nginx-upgrade.8*
%{_unitdir}/nginx.service
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}

%files filesystem
%dir %{nginx_datadir}
%dir %{nginx_datadir}/html
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%dir %{nginx_confdir}/default.d
%dir %{nginx_confdir}/pki
%dir %{nginx_confdir}/sites.d

%changelog

* Tue Sep 01 2015 Stiliyan Sabchew - 123:1.9.4-9
- add plugins:
    - nginx-module-vts
    - ngx_http_dyups_module

* Fri Jul 03 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-6
- switch back to /bin/kill in logrotate script due to SELinux denials

* Tue Jun 16 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-5
- set KillMode=process in systemd service file

* Tue Jun 16 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-4
- fix path to png images in error pages (#1232277)
- optimize png images with optipng

* Sun Jun 14 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-3
- replace /bin/kill with /usr/bin/systemctl kill in logrotate script (#1231543)
- remove After=syslog.target in nginx.service (#1231543)
- replace ExecStop with KillSignal=SIGQUIT in nginx.service (#1231543)
- remove KillMode=mixed as this is not supported on systemd v208

* Sun May 10 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-2
- improve nginx-upgrade
- run nginx-upgrade on package updates
- add TimeoutStopSec=5 and KillMode=mixed to nginx.service
- remove some redundant files
- add some common options to the http block in nginx.conf
- listen on ipv6 for the default server (#1217081)
- remove redundant commands in %%post
- add --with-pcre-jit to configure options

* Thu Apr 09 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.3-1
- update to upstream release 1.6.3

* Wed Oct 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.2-4
- fix package ownership of directories

* Wed Oct 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.2-3
- add vim files (#1142849)

* Mon Sep 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.2-2
- create nginx-filesystem subpackage (patch from Remi Collet)
- create /etc/nginx/default.d as a drop-in directory for configuration files
  for the default server block
- clean up nginx.conf

* Wed Sep 17 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.2-1
- update to upstream release 1.6.2
- CVE-2014-3616 nginx: virtual host confusion (#1142573)

* Wed Aug 27 2014 Jitka Plesnikova <jplesnik@redhat.com> - 1:1.6.1-4
- Perl 5.20 rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Aug 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.1-2
- add logic for EPEL 7

* Tue Aug 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.1-1
- update to upstream release 1.6.1
- (#1126891) CVE-2014-3556: SMTP STARTTLS plaintext injection flaw

* Wed Jul 02 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 1:1.6.0-3
- Fix FTBFS on aarch64 (#1115559)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Apr 26 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.6.0-1
- update to upstream release 1.6.0

* Tue Mar 18 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.7-1
- update to upstream release 1.4.7

* Wed Mar 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.6-1
- update to upstream release 1.4.6

* Sun Feb 16 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.5-2
- avoid multiple index directives (#1065488)

* Sun Feb 16 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.5-1
- update to upstream release 1.4.5

* Wed Nov 20 2013 Peter Borsa <peter.borsa@gmail.com> - 1:1.4.4-1
- Update to upstream release 1.4.4
- Security fix BZ 1032267

* Sun Nov 03 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.3-1
- update to upstream release 1.4.3

* Fri Aug 09 2013 Jonathan Steffan <jsteffan@fedoraproject.org> - 1:1.4.2-3
- Add in conditionals to build for non-systemd targets

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 1:1.4.2-2
- Perl 5.18 rebuild

* Fri Jul 19 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.2-1
- update to upstream release 1.4.2

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1:1.4.1-3
- Perl 5.18 rebuild

* Tue Jun 11 2013 Remi Collet <rcollet@redhat.com> - 1:1.4.1-2
- rebuild for new GD 2.1.0

* Tue May 07 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.1-1
- update to upstream release 1.4.1 (#960605, #960606):
  CVE-2013-2028 stack-based buffer overflow when handling certain chunked
  transfer encoding requests

* Sun Apr 28 2013 Dan Horák <dan[at]danny.cz> - 1:1.4.0-2
- gperftools exist only on selected arches

* Fri Apr 26 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.4.0-1
- update to upstream release 1.4.0
- enable SPDY module (new in this version)
- enable http gunzip module (new in this version)
- enable google perftools module and add gperftools-devel to BR
- enable debugging (#956845)
- trim changelog

* Tue Apr 02 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.8-1
- update to upstream release 1.2.8

* Fri Feb 22 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.7-2
- make sure nginx directories are not world readable (#913724, #913735)

* Sat Feb 16 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.7-1
- update to upstream release 1.2.7
- add .asc file

* Tue Feb 05 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-6
- use 'kill' instead of 'systemctl' when rotating log files to workaround
  SELinux issue (#889151)

* Wed Jan 23 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-5
- uncomment "include /etc/nginx/conf.d/*.conf by default but leave the
  conf.d directory empty (#903065)

* Wed Jan 23 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-4
- add comment in nginx.conf regarding "include /etc/nginf/conf.d/*.conf"
  (#903065)

* Wed Dec 19 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-3
- use correct file ownership when rotating log files

* Tue Dec 18 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-2
- send correct kill signal and use correct file permissions when rotating
  log files (#888225)
- send correct kill signal in nginx-upgrade

* Tue Dec 11 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.6-1
- update to upstream release 1.2.6

* Sat Nov 17 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.5-1
- update to upstream release 1.2.5

* Sun Oct 28 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.4-1
- update to upstream release 1.2.4
- introduce new systemd-rpm macros (#850228)
- link to official documentation not the community wiki (#870733)
- do not run systemctl try-restart after package upgrade to allow the
  administrator to run nginx-upgrade and avoid downtime
- add nginx man page (#870738)
- add nginx-upgrade man page and remove README.fedora
- remove chkconfig from Requires(post/preun)
- remove initscripts from Requires(preun/postun)
- remove separate configuration files in "/etc/nginx/conf.d" directory
  and revert to upstream default of a centralized nginx.conf file
  (#803635) (#842738)

* Fri Sep 21 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.3-1
- update to upstream release 1.2.3

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 28 2012 Petr Pisar <ppisar@redhat.com> - 1:1.2.1-2
- Perl 5.16 rebuild

* Sun Jun 10 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.1-1
- update to upstream release 1.2.1

* Fri Jun 08 2012 Petr Pisar <ppisar@redhat.com> - 1:1.2.0-2
- Perl 5.16 rebuild

* Wed May 16 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.2.0-1
- update to upstream release 1.2.0

* Wed May 16 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.15-4
- add nginx-upgrade to replace functionality from the nginx initscript
  that was lost after migration to systemd
- add README.fedora to describe usage of nginx-upgrade
- nginx.logrotate: use built-in systemd kill command in postrotate script
- nginx.service: start after syslog.target and network.target
- nginx.service: remove unnecessary references to config file location
- nginx.service: use /bin/kill instead of "/usr/sbin/nginx -s" following
  advice from nginx-devel
- nginx.service: use private /tmp

* Mon May 14 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.15-3
- fix incorrect postrotate script in nginx.logrotate

* Thu Apr 19 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.15-2
- renable auto-cc-gcc patch due to warnings on rawhide

* Sat Apr 14 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.15-1
- update to upstream release 1.0.15
- no need to apply auto-cc-gcc patch
- add %%global _hardened_build 1

* Thu Mar 15 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.14-1
- update to upstream release 1.0.14
- amend some %%changelog formatting

* Tue Mar 06 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.13-1
- update to upstream release 1.0.13
- amend --pid-path and --log-path

* Sun Mar 04 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.12-5
- change pid path in nginx.conf to match systemd service file

* Sun Mar 04 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.12-3
- fix %%pre scriptlet

* Mon Feb 20 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:1.0.12-2
- update upstream URL
- replace %%define with %%global
- remove obsolete BuildRoot tag, %%clean section and %%defattr
- remove various unnecessary commands
- add systemd service file and update scriptlets
- add Epoch to accommodate %%triggerun as part of systemd migration

* Sun Feb 19 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.0.12-1
- Update to 1.0.12

* Thu Nov 17 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.10-1
- Bugfix: a segmentation fault might occur in a worker process if resolver got a big DNS response. Thanks to Ben Hawkes.
- Bugfix: in cache key calculation if internal MD5 implementation wasused; the bug had appeared in 1.0.4.
- Bugfix: the module ngx_http_mp4_module sent incorrect "Content-Length" response header line if the "start" argument was used. Thanks to Piotr Sikora.

* Thu Oct 27 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.8-1
- Update to new 1.0.8 stable release

* Fri Aug 26 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.5-1
- Update nginx to Latest Stable Release

* Fri Jun 17 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.0.0-3
- Perl mass rebuild

* Thu Jun 09 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.0.0-2
- Perl 5.14 mass rebuild

* Wed Apr 27 2011 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.0.0-1
- Update to 1.0.0

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.53-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53.5
- Extract out default config into its own file (bug #635776)

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-4
- Revert ownership of log dir

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-3
- Change ownership of /var/log/nginx to be 0700 nginx:nginx
- update init script to use killproc -p
- add reopen_logs command to init script
- update init script to use nginx -q option

* Sun Oct 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-2
- Fix linking of perl module

* Sun Oct 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-1
- Update to new stable 0.8.53

* Sat Jul 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.67-2
- add Provides: webserver (bug #619693)

* Sun Jun 20 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.67-1
- Update to new stable 0.7.67
- fix bugzilla #591543

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 0.7.65-2
- Mass rebuild with perl-5.12.0

* Mon Feb 15 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.65-1
- Update to new stable 0.7.65
- change ownership of logdir to root:root
- add support for ipv6 (bug #561248)
- add random_index_module
- add secure_link_module

* Fri Dec 04 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.64-1
- Update to new stable 0.7.64
